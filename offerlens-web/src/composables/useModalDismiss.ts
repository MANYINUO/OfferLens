import { onBeforeUnmount, watch, type ComponentPublicInstance, type Ref } from 'vue'

/**
 * 模态框可访问性：Esc 关闭、焦点陷阱、关闭后焦点归还。
 *
 * 此前模态框只有点击遮罩关闭，键盘用户打开后按 Esc 无反应，
 * Tab 还能跑到背后的页面上。
 */
const FOCUSABLE = [
  'a[href]',
  'button:not([disabled])',
  'input:not([disabled])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
].join(',')

export function useModalDismiss(open: Ref<boolean>, onClose: () => void) {
  let lastFocused: HTMLElement | null = null
  let container: HTMLElement | null = null

  function focusables(): HTMLElement[] {
    if (!container) return []
    return Array.from(container.querySelectorAll<HTMLElement>(FOCUSABLE)).filter(
      (el) => el.offsetParent !== null || el === document.activeElement,
    )
  }

  function onKeydown(event: KeyboardEvent) {
    if (event.key === 'Escape') {
      event.stopPropagation()
      onClose()
      return
    }
    if (event.key !== 'Tab') return

    const items = focusables()
    if (items.length === 0) return

    const first = items[0]
    const last = items[items.length - 1]
    const active = document.activeElement as HTMLElement | null

    // 焦点跑到容器外时拉回
    if (!container?.contains(active)) {
      event.preventDefault()
      first.focus()
      return
    }
    if (event.shiftKey && active === first) {
      event.preventDefault()
      last.focus()
    } else if (!event.shiftKey && active === last) {
      event.preventDefault()
      first.focus()
    }
  }

  function bind(el: Element | ComponentPublicInstance | null) {
    container = el instanceof HTMLElement ? el : null
  }

  // flush: 'post' 保证在 DOM 更新之后才执行，此时模态框已挂载、ref 已绑定
  watch(
    open,
    (isOpen) => {
      if (isOpen) {
        // 用打开前的元素记录焦点来源；若当前焦点已在模态框内则不覆盖
        const current = document.activeElement as HTMLElement | null
        if (!container?.contains(current)) {
          lastFocused = current
        }
        document.addEventListener('keydown', onKeydown, true)
        document.body.style.overflow = 'hidden'
        // 等一帧确保过渡与布局稳定，再聚焦第一个可交互元素
        requestAnimationFrame(() => {
          const items = focusables()
          // 跳过关闭按钮，直接聚焦第一个输入项，减少用户一次 Tab
          const target = items.find((el) => el.tagName !== 'BUTTON') ?? items[0]
          target?.focus()
        })
      } else {
        document.removeEventListener('keydown', onKeydown, true)
        document.body.style.overflow = ''
        lastFocused?.focus?.()
        lastFocused = null
      }
    },
    { flush: 'post' },
  )

  onBeforeUnmount(() => {
    document.removeEventListener('keydown', onKeydown, true)
    document.body.style.overflow = ''
  })

  return { bind }
}
