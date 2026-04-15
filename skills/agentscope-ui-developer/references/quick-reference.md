# AgentScope Spark Design - Quick Reference

## Package Overview

### @agentscope-ai/design
核心 UI 组件库，基于 Ant Design 5 构建

```bash
npm install @agentscope-ai/design
```

### @agentscope-ai/chat
LLM 对话组件库

```bash
npm install @agentscope-ai/chat
```

---

## Component Categories

### Design Components

| Component | Path | Description |
|-----------|------|-------------|
| Button | `components/Button` | Enhanced button with icon support |
| Modal | `components/Modal` | Dialog with custom animations |
| Select | `components/Select` | Dropdown with search |
| Form | `components/Form` | Form with validation |
| Table | `components/Table` | Data table with sorting |
| StatusBadge | `components/StatusBadge` | Status indicator |

### Chat Components

| Component | Path | Description |
|-----------|------|-------------|
| Bubble | `components/Bubble` | Message bubble |
| Sender | `components/Sender` | Message input |
| Conversations | `components/Conversations` | Chat list |
| ChatAnywhere | `components/ChatAnywhere` | Complete chat container |
| Markdown | `components/Markdown` | Markdown renderer |
| Mermaid | `components/Mermaid` | Diagram renderer |

---

## Theme Tokens

### Color Tokens

```typescript
interface ColorTokens {
  colorPrimary: string;      // Brand primary color
  colorSuccess: string;      // Success state
  colorWarning: string;      // Warning state
  colorError: string;        // Error state
  colorInfo: string;         // Info state
  colorText: string;         // Primary text
  colorTextSecondary: string; // Secondary text
  colorBgContainer: string;  // Container background
  colorBorder: string;       // Border color
}
```

### Spacing Tokens

```typescript
interface SpacingTokens {
  paddingXS: number;   // 8px
  paddingSM: number;   // 12px
  padding: number;     // 16px
  paddingMD: number;   // 20px
  paddingLG: number;   // 24px
  paddingXL: number;   // 32px
}
```

### Typography Tokens

```typescript
interface TypographyTokens {
  fontFamily: string;
  fontSize: number;
  fontSizeSM: number;
  fontSizeLG: number;
  fontWeight: number;
  lineHeight: number;
}
```

---

## Hooks

### useTheme

```tsx
import { useTheme } from 'antd-style';

const MyComponent = () => {
  const theme = useTheme();
  
  return (
    <div style={{ color: theme.token.colorPrimary }}>
      Primary color text
    </div>
  );
};
```

### useStyles (antd-style)

```tsx
import { createStyles } from 'antd-style';

const useStyles = createStyles(({ token, css }) => ({
  container: css`
    padding: ${token.padding}px;
    background: ${token.colorBgContainer};
    border: 1px solid ${token.colorBorder};
  `,
  title: css`
    font-size: ${token.fontSizeLG}px;
    font-weight: ${token.fontWeightStrong};
    color: ${token.colorText};
  `,
}));
```

---

## Common Patterns

### Forward Ref

```tsx
import { forwardRef } from 'react';

export const MyComponent = forwardRef<HTMLDivElement, Props>(
  (props, ref) => (
    <div ref={ref}>{props.children}</div>
  )
);
```

### ClassName Composition

```tsx
import { useStyles } from './style';

const MyComponent = ({ className }) => {
  const { styles, cx } = useStyles();
  
  return (
    <div className={cx(styles.container, className)}>
      Content
    </div>
  );
};
```

### Conditional Rendering

```tsx
const StatusBadge = ({ status, dotOnly }) => {
  const { styles, cx } = useStyles();
  
  return (
    <Badge
      className={cx(
        styles.badge,
        dotOnly && styles.dotOnly
      )}
      status={status}
    />
  );
};
```

---

## Build Commands

```bash
# Development
pnpm run start:spark-design
pnpm run start:spark-chat

# Build
pnpm run build
pnpm run build:spark-design
pnpm run build:spark-chat

# Documentation
pnpm run docs:build
pnpm run docs:build:gh

# Lint
pnpm run lint
pnpm run lint:fix

# Type check
pnpm exec tsc --noEmit
```

---

## File Structure Template

```
ComponentName/
├── index.tsx          # Component implementation
├── style.ts           # antd-style styles
├── index.md           # Dumi documentation
├── demo/
│   ├── basic.tsx      # Basic usage demo
│   ├── size.tsx       # Size variants demo
│   └── disabled.tsx   # Disabled state demo
└── __tests__/
    └── index.test.tsx # Unit tests
```

---

## Common Issues

### 1. Styles Not Applied
- Check if ThemeProvider is wrapping the app
- Verify createStyles is imported from 'antd-style'
- Ensure token values are correct

### 2. Type Errors
- Run `pnpm exec tsc --noEmit` to check types
- Verify all props have proper TypeScript interfaces
- Check for missing imports

### 3. Build Failures
- Delete `node_modules` and `pnpm-lock.yaml`
- Run `pnpm install` again
- Check for circular dependencies

### 4. Hot Reload Not Working
- Restart the dev server
- Check for syntax errors in the component
- Verify the component is properly exported
