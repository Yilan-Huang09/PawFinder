import { expect, test, type APIRequestContext, type Page } from '@playwright/test'

const apiBase = process.env.E2E_API_URL || 'http://127.0.0.1:5000/api/v1'
const password = 'E2ePassword123!'

async function json<T>(response: Awaited<ReturnType<APIRequestContext['post']>>): Promise<T> {
  expect(response.ok(), await response.text()).toBeTruthy()
  return (await response.json()).data as T
}

async function register(request: APIRequestContext, username: string) {
  return json<{ access_token: string; user: { user_id: number } }>(await request.post(`${apiBase}/auth/register`, { data: { username, password } }))
}

async function loginUi(page: Page, username: string) {
  await page.goto('/login')
  await page.locator('input[name="username"]').fill(username)
  await page.locator('input[name="password"]').fill(password)
  await page.getByRole('button', { name: '登录' }).click()
  await expect(page).toHaveURL(/\/pets/)
}

async function switchUser(page: Page, username: string) {
  await page.evaluate(() => localStorage.clear())
  await loginUi(page, username)
}

test('owner, witness and volunteer complete a reunion workflow', async ({ page, request }) => {
  const suffix = `${Date.now()}`.slice(-9)
  const ownerName = `e2e_owner_${suffix}`
  const witnessName = `e2e_witness_${suffix}`
  const volunteerName = `e2e_vol_${suffix}`
  const owner = await register(request, ownerName)
  const witness = await register(request, witnessName)
  await register(request, volunteerName)
  const ownerHeaders = { Authorization: `Bearer ${owner.access_token}` }
  const witnessHeaders = { Authorization: `Bearer ${witness.access_token}` }

  const pet = await json<{ pet_id: number }>(await request.post(`${apiBase}/pets`, {
    headers: ownerHeaders,
    data: { name: '归途', species: 'DOG', breed: 'Border Collie', primary_color: 'BLACK', secondary_color: 'WHITE', gender: 'FEMALE', size: 'MEDIUM', distinctive_features: '胸口白毛，红色项圈' },
  }))
  const lostCase = await json<{ case_id: number }>(await request.post(`${apiBase}/cases`, {
    headers: ownerHeaders,
    data: { pet_id: pet.pet_id, lost_time: new Date(Date.now() - 3 * 3_600_000).toISOString().slice(0, 19), latitude: 30.2741, longitude: 120.1551, address: '端到端测试地铁站', description: '黑白边牧，红色项圈' },
  }))
  await json(await request.post(`${apiBase}/sightings`, {
    headers: witnessHeaders,
    data: { species: 'DOG', breed_guess: 'Border Collie', primary_color: 'BLACK', secondary_color: 'WHITE', gender_guess: 'FEMALE', size_guess: 'MEDIUM', seen_time: new Date(Date.now() - 60 * 60_000).toISOString().slice(0, 19), latitude: 30.276, longitude: 120.1573, address: '端到端测试学院路口', confidence: 5, description: '胸口白毛，戴红色项圈' },
  }))

  await loginUi(page, ownerName)
  await page.goto(`/cases/${lostCase.case_id}/matches`)
  await expect(page.getByText('智能线索匹配')).toBeVisible()
  await page.locator('[data-test="confirm-match"]').first().click()
  await expect(page.getByText('已确认').first()).toBeVisible()

  const area = await json<{ task: { task_id: number } }>(await request.post(`${apiBase}/cases/${lostCase.case_id}/areas`, {
    headers: ownerHeaders,
    data: { area_name: '端到端公园东区', center_latitude: 30.275, center_longitude: 120.156, radius_meters: 600, description: '沿出口与绿道巡查' },
  }))
  await switchUser(page, volunteerName)
  await page.goto(`/cases/${lostCase.case_id}/search`)
  await page.locator(`[data-test="claim-task-${area.task.task_id}"]`).click()
  await page.locator(`[data-test="start-task-${area.task.task_id}"]`).click()
  await page.locator(`textarea[name="task_report_${area.task.task_id}"]`).fill('已完成绿道与出口巡查，未发现其他异常。')
  await page.locator(`[data-test="complete-task-${area.task.task_id}"]`).click()
  await expect(page.getByText('已完成').first()).toBeVisible()

  await switchUser(page, ownerName)
  await page.goto(`/cases/${lostCase.case_id}/search`)
  await page.getByRole('button', { name: '确认寻回', exact: true }).click()
  await page.locator('.search-inline-form--reunion input[type="datetime-local"]').fill(new Date(Date.now() - 60_000).toISOString().slice(0, 16))
  await page.locator('.search-inline-form--reunion input').nth(1).fill('端到端测试寻回点')
  await page.getByRole('button', { name: '确认寻回并归档' }).click()
  await page.goto(`/cases/${lostCase.case_id}`)
  await expect(page.getByText('已寻回').first()).toBeVisible()
})
