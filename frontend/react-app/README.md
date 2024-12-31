frontend/
├── react-app/
│   ├── public/                      # Static assets (favicon, manifest, etc.)
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   ├── manifest.json
│   │   └── robots.txt
│   ├── src/                         # Main source directory
│   │   ├── api/                     # API calls for backend integration
│   │   │   ├── tenantApi.ts         # Tenant API example
│   │   │   ├── schemaApi.ts         # Schema API example
│   │   │   ├── rulesetApi.ts        # Ruleset API example
│   │   │   ├── externalAuthApi.ts   # External authentication API example
│   │   │   └── adminAuthApi.ts      # Admin authentication API example
│   │   ├── components/              # Reusable UI components
│   │   │   ├── Header.tsx           # Header component
│   │   │   ├── Sidebar.tsx          # Sidebar component
│   │   │   ├── Button.tsx           # Button component
│   │   │   └── Input.tsx            # Input component
│   │   ├── pages/                   # Route-specific pages
│   │   │   ├── TenantsPage.tsx      # Tenants page
│   │   │   ├── SchemaPage.tsx       # Schema management page
│   │   │   ├── RulesetPage.tsx      # Ruleset management page
│   │   │   ├── AdminAuthPage.tsx    # Admin authentication page
│   │   │   ├── SandboxAuthPage.tsx  # External authentication test page
│   │   │   ├── SQLGenPage.tsx       # SQL generation page
│   │   │   └── NotFoundPage.tsx     # 404 page
│   │   ├── services/                # Business logic and data handling
│   │   │   ├── tenantService.ts     # Tenant service example
│   │   │   ├── schemaService.ts     # Schema service example
│   │   │   ├── rulesetService.ts    # Ruleset service example
│   │   │   ├── externalAuthService.ts # External auth service
│   │   │   └── adminAuthService.ts  # Admin auth service
│   │   ├── validations/             # Input validations
│   │   │   ├── tenantValidator.ts   # Tenant validations
│   │   │   ├── schemaValidator.ts   # Schema validations
│   │   │   ├── rulesetValidator.ts  # Ruleset validations
│   │   │   └── authValidator.ts     # Auth validations
│   │   ├── hooks/                   # Custom React hooks
│   │   │   ├── useAuth.ts           # Authentication hook
│   │   │   ├── useFetch.ts          # Data fetching hook
│   │   │   └── useChat.ts           # Chat interface hook
│   │   ├── contexts/                # React Context API for global states
│   │   │   ├── AuthContext.tsx      # Authentication context
│   │   │   ├── SandboxContext.tsx   # Sandbox context for external auth
│   │   │   └── ChatContext.tsx      # Chat context
│   │   ├── routes/                  # Application routing
│   │   │   ├── routes.tsx           # Route definitions
│   │   │   ├── PrivateRoute.tsx     # Protected routes for admin
│   │   │   └── PublicRoute.tsx      # Public routes for sandbox
│   │   ├── types/                   # TypeScript type definitions
│   │   │   ├── Tenant.ts            # Tenant types
│   │   │   ├── Schema.ts            # Schema types
│   │   │   ├── Ruleset.ts           # Ruleset types
│   │   │   ├── Auth.ts              # Authentication types
│   │   │   ├── Chat.ts              # Chat types
│   │   │   └── Validation.ts        # Validation types
│   │   ├── utils/                   # Utility functions
│   │   │   ├── formatters.ts        # Formatting utilities
│   │   │   ├── validators.ts        # Generic validators
│   │   │   └── apiHelpers.ts        # API helpers
│   │   ├── styles/                  # Global and component-specific styles
│   │   │   ├── global.scss          # Global styles
│   │   │   ├── variables.scss       # Theme variables
│   │   │   └── components.scss      # Shared component styles
│   │   ├── App.tsx                  # Main React app component
│   │   ├── index.tsx                # React entry point
│   │   ├── react-app-env.d.ts       # React environment definitions
│   │   ├── reportWebVitals.ts       # Performance tracking
│   │   └── setupTests.ts            # Test setup
│   ├── .gitignore
│   ├── package.json                 # React dependencies
│   ├── tsconfig.json                 # TypeScript configuration
│   ├── Dockerfile                    # Frontend Docker configuration
│   ├── docker-compose.yaml           # Docker Compose configuration
│   └── README.md                     # Documentation
