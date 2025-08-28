#!/usr/bin/env python3
from pathlib import Path
from tools.runner.io_utils import write_text, touch_json, MB
import yaml

def run() -> None:
    client_brief = MB / "plan/client_brief.md"
    if not client_brief.exists():
        raise SystemExit("client_brief.md missing; cannot generate backlog.")
    
    # Read client brief content
    brief_content = client_brief.read_text()
    
    # Generate comprehensive product backlog
    product_backlog = generate_product_backlog(brief_content)
    write_text(MB / "plan/product_backlog.yaml", product_backlog, role="product_owner_ai")
    
    # Generate acceptance criteria
    acceptance_criteria = generate_acceptance_criteria(brief_content)
    touch_json(MB / "plan/acceptance_criteria.json", acceptance_criteria, role="product_owner_ai")
    
    # Generate user stories
    user_stories = generate_user_stories(brief_content)
    write_text(MB / "plan/user_stories.md", user_stories, role="product_owner_ai")
    
    # Generate product vision document
    product_vision = generate_product_vision(brief_content)
    write_text(MB / "plan/product_vision.md", product_vision, role="product_owner_ai")

def generate_product_backlog(brief_content: str) -> str:
    """Generate a prioritized product backlog based on the client brief."""
    
    backlog = """# Product Backlog - Customer Support Ticket Dashboard

## Epic: Core Dashboard Functionality
**Priority: HIGH** | **Story Points: 21**

### User Story 1: Dashboard Overview
**As a** support team member  
**I want to** see all incoming tickets at a glance  
**So that** I can quickly assess workload and prioritize my work

**Acceptance Criteria:**
- [ ] Display total ticket count
- [ ] Show tickets by status (New, In Progress, Resolved, Closed)
- [ ] Show tickets by priority (Low, Medium, High, Critical)
- [ ] Real-time updates without page refresh

**Story Points: 5**

### User Story 2: Ticket Filtering
**As a** support team member  
**I want to** filter tickets by various criteria  
**So that** I can focus on specific types of tickets

**Acceptance Criteria:**
- [ ] Filter by priority level
- [ ] Filter by status
- [ ] Filter by assignee
- [ ] Filter by date range
- [ ] Search by ticket title/description
- [ ] Save custom filter combinations

**Story Points: 8**

### User Story 3: Ticket Assignment
**As a** support team lead  
**I want to** assign tickets to specific agents  
**So that** workload is distributed evenly and efficiently

**Acceptance Criteria:**
- [ ] Drag-and-drop ticket assignment
- [ ] Bulk assignment for multiple tickets
- [ ] Assignment history tracking
- [ ] Agent workload indicators
- [ ] Auto-assignment based on agent skills

**Story Points: 8**

## Epic: Authentication & User Management
**Priority: HIGH** | **Story Points: 13**

### User Story 4: User Authentication
**As a** support team member  
**I want to** securely log into the dashboard  
**So that** I can access my assigned tickets

**Acceptance Criteria:**
- [ ] JWT-based authentication
- [ ] Secure login/logout functionality
- [ ] Password reset capability
- [ ] Session timeout handling
- [ ] Multi-factor authentication (optional)

**Story Points: 5**

### User Story 5: User Role Management
**As a** system administrator  
**I want to** manage user roles and permissions  
**So that** different team members have appropriate access levels

**Acceptance Criteria:**
- [ ] Role-based access control
- [ ] Admin, Lead, and Agent roles
- [ ] Permission management per role
- [ ] User account creation/deactivation

**Story Points: 8**

## Epic: Notification System
**Priority: MEDIUM** | **Story Points: 13**

### User Story 6: Email Notifications
**As a** support team member  
**I want to** receive email notifications for ticket updates  
**So that** I stay informed about changes without constantly checking the dashboard

**Acceptance Criteria:**
- [ ] New ticket notifications
- [ ] Status change notifications
- [ ] Assignment notifications
- [ ] Comment notifications
- [ ] Configurable notification preferences

**Story Points: 8**

### User Story 7: Slack Integration
**As a** support team member  
**I want to** receive Slack notifications for critical updates  
**So that** I can respond quickly to urgent matters

**Acceptance Criteria:**
- [ ] Slack webhook integration
- [ ] Critical ticket alerts
- [ ] Escalation notifications
- [ ] Customizable notification rules

**Story Points: 5**

## Epic: Responsive Design
**Priority: MEDIUM** | **Story Points: 8**

### User Story 8: Mobile & Tablet Support
**As a** support team member  
**I want to** access the dashboard from any device  
**So that** I can work efficiently regardless of location

**Acceptance Criteria:**
- [ ] Responsive design for desktop, tablet, and mobile
- [ ] Touch-friendly interface for mobile devices
- [ ] Optimized layouts for different screen sizes
- [ ] Consistent user experience across devices

**Story Points: 8**

## Epic: Testing & Quality Assurance
**Priority: MEDIUM** | **Story Points: 5**

### User Story 9: Comprehensive Testing
**As a** development team  
**I want to** ensure the dashboard is thoroughly tested  
**So that** we deliver a high-quality, bug-free product

**Acceptance Criteria:**
- [ ] Unit tests with Jest (minimum 80% coverage)
- [ ] Integration tests for API endpoints
- [ ] End-to-end tests for critical user flows
- [ ] Performance testing for dashboard load times
- [ ] Security testing for authentication flows

**Story Points: 5**

## Epic: Deployment & Documentation
**Priority: LOW** | **Story Points: 5**

### User Story 10: Staging Deployment
**As a** development team  
**I want to** deploy to a staging environment  
**So that** we can test the dashboard before production release

**Acceptance Criteria:**
- [ ] Docker containerization
- [ ] Vercel deployment configuration
- [ ] Environment-specific configurations
- [ ] Automated deployment pipeline

**Story Points: 3**

### User Story 11: Documentation
**As a** support team  
**I want to** have comprehensive documentation  
**So that** I can effectively use and maintain the dashboard

**Acceptance Criteria:**
- [ ] User manual for support team
- [ ] API documentation for developers
- [ ] Setup and installation guide
- [ ] Troubleshooting guide

**Story Points: 2**

## Total Story Points: 65
## Estimated Duration: 10-14 working days
## Risk Level: MEDIUM

## Definition of Done
- [ ] Code reviewed and approved
- [ ] Unit tests passing with >80% coverage
- [ ] Integration tests passing
- [ ] User acceptance testing completed
- [ ] Performance requirements met
- [ ] Security requirements validated
- [ ] Documentation updated
- [ ] Staging deployment successful
"""
    
    return backlog

def generate_acceptance_criteria(brief_content: str) -> dict:
    """Generate detailed acceptance criteria for each user story."""
    
    criteria = {
        "criteria": [
            {
                "story_id": "US1",
                "title": "Dashboard Overview",
                "criteria": [
                    "Dashboard displays total ticket count prominently",
                    "Tickets are grouped by status with clear visual indicators",
                    "Priority levels are color-coded (Red=Critical, Orange=High, Yellow=Medium, Green=Low)",
                    "Real-time updates occur within 5 seconds of data changes",
                    "Dashboard loads within 3 seconds on standard internet connection"
                ]
            },
            {
                "story_id": "US2", 
                "title": "Ticket Filtering",
                "criteria": [
                    "All filter options are clearly visible and accessible",
                    "Filters can be combined (e.g., High Priority + In Progress)",
                    "Search function returns results within 1 second",
                    "Filter combinations can be saved and named",
                    "Clear visual feedback shows active filters"
                ]
            },
            {
                "story_id": "US3",
                "title": "Ticket Assignment", 
                "criteria": [
                    "Drag-and-drop assignment works smoothly on desktop",
                    "Bulk assignment handles up to 50 tickets simultaneously",
                    "Assignment history shows who assigned what and when",
                    "Agent workload indicators update in real-time",
                    "Auto-assignment considers agent skills and current workload"
                ]
            },
            {
                "story_id": "US4",
                "title": "User Authentication",
                "criteria": [
                    "Login process completes within 2 seconds",
                    "JWT tokens expire after 8 hours of inactivity",
                    "Password reset emails are sent within 1 minute",
                    "Failed login attempts are logged for security monitoring",
                    "Session timeout warnings appear 5 minutes before expiration"
                ]
            },
            {
                "story_id": "US5",
                "title": "User Role Management",
                "criteria": [
                    "Role changes take effect immediately upon save",
                    "Permission changes are logged for audit purposes",
                    "Admin can create new users with appropriate roles",
                    "Role hierarchy prevents privilege escalation",
                    "User deactivation preserves ticket history"
                ]
            },
            {
                "story_id": "US6",
                "title": "Email Notifications",
                "criteria": [
                    "Emails are delivered within 5 minutes of triggering event",
                    "Notification preferences are saved per user",
                    "Email templates are professional and clear",
                    "Unsubscribe options are available for non-critical notifications",
                    "Email delivery failures are logged and retried"
                ]
            },
            {
                "story_id": "US7",
                "title": "Slack Integration",
                "criteria": [
                    "Slack messages are delivered within 1 minute",
                    "Webhook failures are logged and retried automatically",
                    "Critical alerts include actionable information",
                    "Escalation notifications follow defined rules",
                    "Slack integration can be disabled per user preference"
                ]
            },
            {
                "story_id": "US8",
                "title": "Mobile & Tablet Support",
                "criteria": [
                    "Dashboard is fully functional on devices with 320px+ width",
                    "Touch targets are at least 44px in size",
                    "Navigation is intuitive on mobile devices",
                    "Performance is maintained across all device types",
                    "User experience is consistent regardless of device"
                ]
            },
            {
                "story_id": "US9",
                "title": "Comprehensive Testing",
                "criteria": [
                    "Unit test coverage exceeds 80% for all modules",
                    "Integration tests cover all API endpoints",
                    "E2E tests validate critical user journeys",
                    "Performance tests meet defined response time requirements",
                    "Security tests validate authentication and authorization"
                ]
            },
            {
                "story_id": "US10",
                "title": "Staging Deployment",
                "criteria": [
                    "Docker containers start within 30 seconds",
                    "Vercel deployment completes within 5 minutes",
                    "Environment variables are properly configured",
                    "Deployment pipeline includes automated testing",
                    "Rollback capability is available if deployment fails"
                ]
            },
            {
                "story_id": "US11",
                "title": "Documentation",
                "criteria": [
                    "User manual covers all dashboard features",
                    "API documentation includes examples and error codes",
                    "Setup guide includes troubleshooting steps",
                    "Documentation is searchable and well-organized",
                    "Documentation is updated with each release"
                ]
            }
        ]
    }
    
    return criteria

def generate_user_stories(brief_content: str) -> str:
    """Generate detailed user stories with acceptance criteria."""
    
    stories = """# User Stories - Customer Support Ticket Dashboard

## Epic 1: Core Dashboard Functionality

### US1: Dashboard Overview
**As a** support team member  
**I want to** see all incoming tickets at a glance  
**So that** I can quickly assess workload and prioritize my work

**Acceptance Criteria:**
- [ ] Display total ticket count prominently at the top of the dashboard
- [ ] Show tickets grouped by status with clear visual indicators
- [ ] Display priority levels with color coding (Red=Critical, Orange=High, Yellow=Medium, Green=Low)
- [ ] Real-time updates occur within 5 seconds of data changes
- [ ] Dashboard loads within 3 seconds on standard internet connection

**Story Points:** 5  
**Priority:** HIGH  
**Dependencies:** None

---

### US2: Ticket Filtering
**As a** support team member  
**I want to** filter tickets by various criteria  
**So that** I can focus on specific types of tickets

**Acceptance Criteria:**
- [ ] Filter by priority level (Low, Medium, High, Critical)
- [ ] Filter by status (New, In Progress, Resolved, Closed)
- [ ] Filter by assignee (All, Unassigned, Specific Agent)
- [ ] Filter by date range (Today, This Week, This Month, Custom Range)
- [ ] Search by ticket title or description text
- [ ] Save custom filter combinations with descriptive names
- [ ] Clear visual feedback shows which filters are currently active

**Story Points:** 8  
**Priority:** HIGH  
**Dependencies:** US1 (Dashboard Overview)

---

### US3: Ticket Assignment
**As a** support team lead  
**I want to** assign tickets to specific agents  
**So that** workload is distributed evenly and efficiently

**Acceptance Criteria:**
- [ ] Drag-and-drop ticket assignment from unassigned to agent columns
- [ ] Bulk assignment for multiple tickets (up to 50 at once)
- [ ] Assignment history tracking (who assigned what and when)
- [ ] Agent workload indicators showing current ticket count
- [ ] Auto-assignment based on agent skills and current workload
- [ ] Assignment confirmation with option to add notes

**Story Points:** 8  
**Priority:** HIGH  
**Dependencies:** US1 (Dashboard Overview)

---

## Epic 2: Authentication & User Management

### US4: User Authentication
**As a** support team member  
**I want to** securely log into the dashboard  
**So that** I can access my assigned tickets

**Acceptance Criteria:**
- [ ] JWT-based authentication with secure token storage
- [ ] Secure login/logout functionality with proper session management
- [ ] Password reset capability with email verification
- [ ] Session timeout handling with user warnings
- [ ] Multi-factor authentication option for enhanced security
- [ ] Failed login attempt logging and rate limiting

**Story Points:** 5  
**Priority:** HIGH  
**Dependencies:** None

---

### US5: User Role Management
**As a** system administrator  
**I want to** manage user roles and permissions  
**So that** different team members have appropriate access levels

**Acceptance Criteria:**
- [ ] Role-based access control with predefined roles (Admin, Lead, Agent)
- [ ] Permission management per role (read, write, assign, delete)
- [ ] User account creation with role assignment
- [ ] User account deactivation with data preservation
- [ ] Role hierarchy prevents privilege escalation
- [ ] Permission changes are logged for audit purposes

**Story Points:** 8  
**Priority:** HIGH  
**Dependencies:** US4 (User Authentication)

---

## Epic 3: Notification System

### US6: Email Notifications
**As a** support team member  
**I want to** receive email notifications for ticket updates  
**So that** I stay informed about changes without constantly checking the dashboard

**Acceptance Criteria:**
- [ ] New ticket notifications sent to appropriate team members
- [ ] Status change notifications for assigned tickets
- [ ] Assignment notifications when tickets are assigned
- [ ] Comment notifications for ticket discussions
- [ ] Configurable notification preferences per user
- [ ] Professional email templates with clear call-to-action

**Story Points:** 8  
**Priority:** MEDIUM  
**Dependencies:** US3 (Ticket Assignment)

---

### US7: Slack Integration
**As a** support team member  
**I want to** receive Slack notifications for critical updates  
**So that** I can respond quickly to urgent matters

**Acceptance Criteria:**
- [ ] Slack webhook integration for real-time notifications
- [ ] Critical ticket alerts for high-priority issues
- [ ] Escalation notifications for overdue tickets
- [ ] Customizable notification rules and channels
- [ ] Integration can be disabled per user preference

**Story Points:** 5  
**Priority:** MEDIUM  
**Dependencies:** US6 (Email Notifications)

---

## Epic 4: Responsive Design

### US8: Mobile & Tablet Support
**As a** support team member  
**I want to** access the dashboard from any device  
**So that** I can work efficiently regardless of location

**Acceptance Criteria:**
- [ ] Responsive design works on desktop, tablet, and mobile devices
- [ ] Touch-friendly interface for mobile devices with appropriate touch targets
- [ ] Optimized layouts for different screen sizes (320px+ width)
- [ ] Consistent user experience across all device types
- [ ] Performance maintained across all device types

**Story Points:** 8  
**Priority:** MEDIUM  
**Dependencies:** US1 (Dashboard Overview)

---

## Epic 5: Testing & Quality Assurance

### US9: Comprehensive Testing
**As a** development team  
**I want to** ensure the dashboard is thoroughly tested  
**So that** we deliver a high-quality, bug-free product

**Acceptance Criteria:**
- [ ] Unit tests with Jest achieving minimum 80% code coverage
- [ ] Integration tests covering all API endpoints and database operations
- [ ] End-to-end tests validating critical user flows
- [ ] Performance testing ensuring dashboard loads within defined time limits
- [ ] Security testing validating authentication and authorization flows

**Story Points:** 5  
**Priority:** MEDIUM  
**Dependencies:** All development stories

---

## Epic 6: Deployment & Documentation

### US10: Staging Deployment
**As a** development team  
**I want to** deploy to a staging environment  
**So that** we can test the dashboard before production release

**Acceptance Criteria:**
- [ ] Docker containerization with optimized image sizes
- [ ] Vercel deployment configuration for frontend
- [ ] Environment-specific configurations for staging vs production
- [ ] Automated deployment pipeline with testing gates
- [ ] Rollback capability if deployment fails

**Story Points:** 3  
**Priority:** LOW  
**Dependencies:** US9 (Comprehensive Testing)

---

### US11: Documentation
**As a** support team  
**I want to** have comprehensive documentation  
**So that** I can effectively use and maintain the dashboard

**Acceptance Criteria:**
- [ ] User manual covering all dashboard features and workflows
- [ ] API documentation with examples, error codes, and authentication details
- [ ] Setup and installation guide for development and deployment
- [ ] Troubleshooting guide for common issues
- [ ] Documentation is searchable, well-organized, and regularly updated

**Story Points:** 2  
**Priority:** LOW  
**Dependencies:** US10 (Staging Deployment)

---

## Story Point Summary
- **Total Story Points:** 65
- **High Priority Stories:** 34 points
- **Medium Priority Stories:** 26 points  
- **Low Priority Stories:** 5 points

## Sprint Planning Recommendations
- **Sprint 1 (Weeks 1-2):** Epic 1 (Core Dashboard) + Epic 2 (Authentication) = 47 points
- **Sprint 2 (Weeks 3-4):** Epic 3 (Notifications) + Epic 4 (Responsive Design) = 34 points
- **Sprint 3 (Weeks 5-6):** Epic 5 (Testing) + Epic 6 (Deployment) = 7 points

## Risk Mitigation
- **Technical Risk:** Start with authentication and core dashboard to establish foundation
- **Timeline Risk:** Prioritize high-value features for early delivery
- **Quality Risk:** Include testing story in each sprint for continuous validation
"""
    
    return stories

def generate_product_vision(brief_content: str) -> str:
    """Generate a comprehensive product vision document."""
    
    vision = """# Product Vision - Customer Support Ticket Dashboard

## Vision Statement
**"Empower support teams with an intuitive, real-time dashboard that transforms ticket management from reactive to proactive, enabling faster resolution and better customer satisfaction."**

## Product Overview
The Customer Support Ticket Dashboard is a web-based solution designed to centralize and streamline support ticket management. It provides support teams with a comprehensive view of all incoming tickets, efficient assignment capabilities, and real-time tracking until resolution.

## Target Users

### Primary Users
- **Support Team Members:** Daily users who manage and resolve tickets
- **Support Team Leads:** Supervisors who assign tickets and monitor team performance
- **System Administrators:** IT staff who manage user accounts and system configuration

### Secondary Users
- **Customer Success Managers:** Stakeholders who need visibility into support metrics
- **Product Managers:** Teams who use support data for product improvements

## Business Objectives

### Primary Goals
1. **Reduce Ticket Resolution Time:** Streamline workflow to resolve tickets 30% faster
2. **Improve Team Efficiency:** Eliminate manual processes and reduce administrative overhead
3. **Enhance Customer Satisfaction:** Provide faster, more consistent support responses
4. **Increase Team Productivity:** Enable support agents to handle 25% more tickets

### Success Metrics
- **Time to First Response:** < 2 hours for high-priority tickets
- **Ticket Resolution Time:** < 24 hours for 80% of tickets
- **Team Productivity:** 25% increase in tickets handled per agent
- **Customer Satisfaction:** Maintain or improve existing CSAT scores

## Key Features & Capabilities

### Core Functionality
- **Real-time Dashboard:** Live view of all tickets with instant updates
- **Smart Filtering:** Advanced search and filter capabilities for efficient ticket management
- **Intelligent Assignment:** Automated and manual ticket assignment with workload balancing
- **Status Tracking:** Complete visibility into ticket lifecycle from creation to resolution

### User Experience
- **Responsive Design:** Seamless experience across desktop, tablet, and mobile devices
- **Intuitive Interface:** Clean, modern design that requires minimal training
- **Real-time Updates:** Instant notifications and live data without page refreshes
- **Accessibility:** WCAG 2.1 AA compliance for inclusive design

### Integration & Notifications
- **Email System:** Automated notifications for ticket updates and assignments
- **Slack Integration:** Real-time alerts for critical updates and escalations
- **API Access:** RESTful API for integration with existing systems
- **Webhook Support:** Extensible notification system for custom integrations

## Technical Requirements

### Performance Standards
- **Page Load Time:** < 3 seconds for dashboard initialization
- **Real-time Updates:** < 5 seconds for data synchronization
- **Concurrent Users:** Support for 100+ simultaneous users
- **Uptime:** 99.9% availability during business hours

### Security Requirements
- **Authentication:** JWT-based secure authentication system
- **Authorization:** Role-based access control with granular permissions
- **Data Protection:** Encrypted data transmission and secure storage
- **Audit Logging:** Comprehensive activity tracking for compliance

### Scalability Considerations
- **Database Design:** Optimized schema for high-volume ticket processing
- **Caching Strategy:** Intelligent caching for improved performance
- **Load Balancing:** Support for horizontal scaling as user base grows
- **API Design:** RESTful architecture for easy integration and expansion

## Competitive Advantages

### Differentiation Factors
1. **Real-time Performance:** Instant updates and live data synchronization
2. **Intelligent Automation:** Smart assignment and workflow optimization
3. **Mobile-First Design:** Responsive interface optimized for all devices
4. **Extensible Architecture:** Easy integration with existing tools and systems

### Market Position
- **Target Market:** Small to medium-sized support teams (5-50 agents)
- **Price Point:** Competitive pricing with clear value proposition
- **Deployment Model:** Cloud-based SaaS with optional on-premise options
- **Support Model:** Comprehensive documentation and responsive support

## Future Roadmap

### Phase 2 Features (3-6 months)
- **Advanced Analytics:** Detailed reporting and performance metrics
- **Workflow Automation:** Customizable ticket routing and escalation rules
- **Knowledge Base Integration:** Built-in knowledge management system
- **Customer Portal:** Self-service ticket creation and tracking

### Phase 3 Features (6-12 months)
- **AI-Powered Insights:** Machine learning for ticket classification and routing
- **Advanced Reporting:** Custom dashboards and executive summaries
- **Multi-language Support:** Internationalization for global teams
- **Mobile App:** Native mobile applications for iOS and Android

## Success Criteria

### Launch Success
- [ ] Dashboard successfully deployed to staging environment
- [ ] All core features functional and tested
- [ ] Support team trained and ready for production use
- [ ] Performance benchmarks met or exceeded

### Adoption Success
- [ ] 90% of support team using dashboard within first week
- [ ] Positive user feedback and satisfaction scores
- [ ] Measurable improvement in ticket resolution times
- [ ] Successful integration with existing notification systems

### Business Impact
- [ ] 30% reduction in average ticket resolution time
- [ ] 25% increase in team productivity metrics
- [ ] Improved customer satisfaction scores
- [ ] Reduced administrative overhead and manual processes

## Risk Assessment

### Technical Risks
- **Integration Complexity:** Mitigation through phased implementation and thorough testing
- **Performance Issues:** Mitigation through performance testing and optimization
- **Security Vulnerabilities:** Mitigation through security review and penetration testing

### Business Risks
- **User Adoption:** Mitigation through training and change management
- **Timeline Delays:** Mitigation through agile development and regular checkpoints
- **Scope Creep:** Mitigation through clear requirements and change control process

## Conclusion
The Customer Support Ticket Dashboard represents a significant step forward in support team efficiency and customer service quality. By providing real-time visibility, intelligent automation, and seamless user experience, this solution will transform how support teams operate and deliver value to customers.

The phased approach ensures successful delivery while managing risks and providing immediate value to users. With clear success metrics and a comprehensive roadmap, this project is positioned for long-term success and continued enhancement.
"""
    
    return vision

