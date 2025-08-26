# React Domain Knowledge
# React.js development standards and best practices

## Core Principles
- **Component-Based Architecture**: Build reusable, composable components
- **Unidirectional Data Flow**: Data flows down, events flow up
- **Virtual DOM**: Efficient rendering and updates
- **JSX**: JavaScript XML for component structure
- **Hooks**: Functional components with state and lifecycle

## Best Practices
```typescript
// Component Structure
interface ComponentProps {
  title: string;
  onAction: (data: any) => void;
  children?: React.ReactNode;
}

const MyComponent: React.FC<ComponentProps> = ({ 
  title, 
  onAction, 
  children 
}) => {
  const [state, setState] = useState<StateType>(initialState);
  
  useEffect(() => {
    // Side effects and cleanup
    return () => {
      // Cleanup function
    };
  }, [dependencies]);
  
  return (
    <div className="component">
      <h1>{title}</h1>
      {children}
    </div>
  );
};
```

## State Management
- **Local State**: useState for component-level state
- **Context API**: Global state for small applications
- **Redux Toolkit**: Complex state management
- **Zustand**: Lightweight state management
- **React Query**: Server state management

## Performance Optimization
- **React.memo**: Prevent unnecessary re-renders
- **useMemo**: Memoize expensive calculations
- **useCallback**: Memoize function references
- **Code Splitting**: Lazy loading with React.lazy
- **Virtualization**: Handle large lists efficiently

## Testing Strategy
- **Jest**: Unit testing framework
- **React Testing Library**: Component testing utilities
- **Cypress**: End-to-end testing
- **Storybook**: Component development and testing

## Code Quality Standards
- **ESLint**: Code linting and style enforcement
- **Prettier**: Code formatting
- **TypeScript**: Type safety and better developer experience
- **PropTypes**: Runtime type checking (for non-TypeScript projects)

## Integration Patterns
- **API Integration**: Axios, React Query, SWR
- **Routing**: React Router for navigation
- **Forms**: React Hook Form, Formik
- **Styling**: CSS Modules, Styled Components, Tailwind CSS
- **Build Tools**: Vite, Create React App, Next.js
