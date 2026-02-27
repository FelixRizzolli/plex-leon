import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import AppButton from '@components/ui/AppButton.vue'

describe('AppButton', () => {
  it('renders default slot content', () => {
    const wrapper = mount(AppButton, {
      global: { plugins: [createPinia()] },
      slots: { default: 'Click me' },
    })
    expect(wrapper.text()).toBe('Click me')
  })

  it('applies primary variant class by default', () => {
    const wrapper = mount(AppButton, {
      global: { plugins: [createPinia()] },
    })
    expect(wrapper.classes()).toContain('app-btn--primary')
  })

  it('applies custom variant class', () => {
    const wrapper = mount(AppButton, {
      global: { plugins: [createPinia()] },
      props: { variant: 'danger' },
    })
    expect(wrapper.classes()).toContain('app-btn--danger')
  })

  it('emits click event when clicked', async () => {
    const wrapper = mount(AppButton, {
      global: { plugins: [createPinia()] },
    })
    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
  })

  it('does not emit click when disabled', async () => {
    const wrapper = mount(AppButton, {
      global: { plugins: [createPinia()] },
      props: { disabled: true },
    })
    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeFalsy()
  })

  it('shows spinner when loading', () => {
    const wrapper = mount(AppButton, {
      global: { plugins: [createPinia()] },
      props: { loading: true },
    })
    expect(wrapper.find('.spinner').exists()).toBe(true)
  })
})
