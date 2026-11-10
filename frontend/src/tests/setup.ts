import { afterEach } from 'vitest'

afterEach(() => {
  localStorage.clear()
})

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => undefined,
    removeListener: () => undefined,
    addEventListener: () => undefined,
    removeEventListener: () => undefined,
    dispatchEvent: () => false,
  }),
})

class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}

globalThis.ResizeObserver = ResizeObserverMock

Object.defineProperty(window, 'scrollTo', {
  writable: true,
  value: () => undefined,
})

Object.defineProperty(URL, 'createObjectURL', {
  writable: true,
  value: () => 'blob:pawfinder-test-preview',
})

Object.defineProperty(URL, 'revokeObjectURL', {
  writable: true,
  value: () => undefined,
})
