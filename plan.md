# Site Management & Deployment Panel - Detailed Implementation Plan

## Project Overview

A comprehensive web-based admin panel that enables users to create, manage, generate, and deploy affiliate websites to Cloudflare Pages. The system integrates AI-powered content generation (ChatGPT, Grok), dynamic template processing, advanced media handling, and built-in analytics (Umami).

---

## Part 1: System Architecture & Infrastructure

### 1.1 Technology Stack

**Backend**
- Primary Framework: Django with Django REST Framework
- Async Task Queue: Celery with Redis broker
- Real-time Communication: Django Channels (for preview updates)
- Database: PostgreSQL (for multi-user data integrity)
- Static Site Generation: Custom Python-based generator

**Frontend**
- Framework: React with TypeScript
- UI Components: Material-UI or custom component library
- State Management: Redux or Zustand
- API Client: Axios with TypeScript typings

**Infrastructure**
- Web Server: Gunicorn/uWSGI
- Reverse Proxy: Nginx
- Container Orchestration: Docker + Docker Compose
- File Storage: Local filesystem or S3-compatible (MinIO)
- Task Queue: Redis

### 1.2 Database Architecture

**Core Entities**
- Users (with role-based access control: Admin, User)
- Sites (domain configuration, branding, settings)
- Templates (monolithic and sectional types)
- Pages (per-site content structure)
- Blocks (content blocks within pages: Hero, Article, Image, CTA, FAQ, Swiper)
- Media Library (images organized in folders)
- Prompts (AI generation templates)
- CloudflareTokens (API credentials with usage tracking)
- LanguagePresets (supported languages: en-EN, fr-FR, etc.)
- AffiliateLinks (preset partner links)
- Deployments (deployment history and rollback data)

**Key Relationships**
- User → Sites (one-to-many)
- Site → Pages (one-to-many)
- Page → Blocks (one-to-many)
- Template → TemplateVariables (one-to-many)
- Site → MediaLibraryFolder (one-to-many)
- User → Prompts (one-to-many)
- Site → Deployments (one-to-many)

---

## Part 2: User Management & Authentication

### 2.1 Role-Based Access Control

**Admin Users**
- View and manage all sites across all users
- Create, edit, delete users
- Configure system settings (languages, tokens, prompts, templates)
- Access analytics for all sites
- View deployment logs

**Regular Users**
- View and manage only their own sites
- Create new sites within quota limits
- Cannot modify system settings
- Cannot view other users' sites or analytics

### 2.2 Authentication Flow

**Login System**
- Email and password-based authentication
- JWT token generation (access + refresh tokens)
- Session timeout after inactivity
- Remember-me functionality (optional)

**Security Measures**
- Password hashing with bcrypt
- CSRF protection
- Rate limiting on login attempts
- Audit logging for sensitive operations

---

## Part 3: Settings & Configuration

### 3.1 Global Settings (Admin Only)

**Language Management**
- Add/remove supported languages (format: en-EN, fr-FR, de-DE, etc.)
- Each language stored as a preset for quick site creation
- Support for multiple locales

**API Token Management**
- ChatGPT/OpenAI tokens (with model selection: GPT-4, GPT-3.5, etc.)
- Grok API tokens
- Cloudflare API tokens (with site count tracking per token)
- Token encryption and secure storage
- Token usage statistics and quota monitoring

**Affiliate Links**
- Preset partner links globally configurable
- Each link can be selected during site creation
- Links applied to all active CTA buttons on the site
- Support for dynamic URL parameters

**Media Library Access Controls**
- Configure default media folder per user
- Bulk upload capabilities
- Folder organization preferences

### 3.2 Prompt Management

**Text Generation Prompts**
- Prompt Name (human-readable identifier)
- Prompt Type (target content: article, title, description, H1, FAQ, hero)
- AI Model Selection (ChatGPT, Grok)
- Temperature Setting (0-1 scale for creativity control)
- Prompt Content (full instruction text)
- Input Variables (e.g., {{keywords}}, {{lsi_phrases}}, {{brand}})
- Output Format Specification (HTML, Markdown, plain text)

**Image Generation Prompts**
- DALL-E or Midjourney integration preparation
- Prompt templates for different image types
- Style presets (realistic, illustrated, minimalist)
- Size and format specifications

---

## Part 4: Template System

### 4.1 Template Types

**Monolithic Templates**
- Fixed structure that cannot be modified
- Brand-specific (immutable layout)
- Pre-defined block order and styling
- Faster rendering and more predictable output
- Use case: corporate branding requirements

**Sectional Templates**
- Modular, component-based approach
- Reusable sections (header, footer, sidebar, content areas)
- Sections can be combined in various configurations
- More flexible for different content types
- Use case: content variation without complete redesign

### 4.2 Template Upload & Storage

**Monolithic Template Package Contents**
- HTML base file (with template variables)
- CSS stylesheet(s)
- JavaScript files
- Sample header menu structure
- Sample footer menu structure
- FAQ block template
- Assets folder with placeholder images
- Configuration file (JSON) describing available variables

**Sectional Template Package Contents**
- Base HTML wrapper
- Modular section components (header, footer, sidebar, main content)
- CSS for each section
- Component configuration file
- Default styling and color schemes

### 4.3 Template Variables & Substitution Engine

**Standard Variables**
- `{{SITE_BRAND}}` - Brand name
- `{{SITE_DOMAIN}}` - Domain name (without trailing slash)
- `{{SITE_LANGUAGE}}` - Language code
- `{{AFFILIATE_LINK}}` - Preset affiliate link
- `{{PAGE_TITLE}}` - Page meta title
- `{{PAGE_DESCRIPTION}}` - Page meta description
- `{{PAGE_H1}}` - Page H1 heading
- `{{PAGE_CANONICAL}}` - Canonical URL
- `{{LOGO_URL}}` - Path to logo image
- `{{FAVICON_LINKS}}` - All favicon link tags
- `{{METADATA}}` - All meta tags and structured data
- `{{MICRODATA}}` - JSON-LD and structured markup
- `{{STYLES_INLINE}}` - CSS content inline or linked
- `{{SCRIPTS_INLINE}}` - JavaScript content inline or linked
- `{{CONTENT}}` - Main page content from blocks
- `{{HEADER_MENU}}` - Generated header navigation
- `{{FOOTER_MENU}}` - Generated footer navigation
- `{{FOOTER_IMAGES}}` - Footer images (payment methods, providers)

**Variable Injection Modes**
- Direct inline content
- External file reference (for CSS/JS)
- Async loading via script tags
- Path-only (for custom loading)

### 4.4 Fingerprinting System

**Purpose**: Generate unique website variants for SEO diversity and to avoid detection as generated sites.

**Fingerprinting Components**

**CSS Class Randomization**
- Generate random class names for each site (e.g., `_1jhy4_gtw2n _10uta_gtw2n`)
- Apply to all stylesheet classes and inline styles
- Maintain class consistency within same site
- Deterministic randomization (seed-based for reproducibility)

**CMS-Specific Footprints**
- WordPress (wp-content/themes/theme-name/assets/)
- Joomla (components/templates/)
- Custom CMS (generic structure)
- Each footprint includes CMS-specific file hierarchy
- Automatic path replacement based on selected footprint

**Image Optimization for Fingerprinting**
- Vary image sizes across sites (384x384, 400x400, 412x412, etc.)
- Different compression levels per site
- Format variations (WebP, PNG, JPEG with different quality)
- Slight dimension variations (±1-2%)

**Custom Class List Option**
- Alternative to random generation
- Admin can define preset class naming schemes
- Each scheme contains custom class names (one per line)
- Site creator selects preferred scheme during site generation
- System applies chosen scheme instead of random generation

---

## Part 5: Media Library

### 5.1 Media Library Structure

**Organization**
- Hierarchical folder system (unlimited nesting)
- Per-user media libraries (separate from other users)
- Per-site optional dedicated subfolder
- Bulk folder operations (create, rename, delete)

### 5.2 Image Upload Methods

**Method 1: Direct Upload from Library**
- Browse organized folders
- Search by filename
- Preview before selection
- Per-site image renaming (different name per site, same file)
- Per-site Alt text and Title customization

**Method 2: URL-based Upload**
- Paste image URL from external source
- System downloads and stores locally
- Filename specification by user
- Alt text input by user
- Automatic media library storage

**Method 3: Clipboard Paste**
- Copy image from browser/application (Ctrl+C)
- Paste directly into image input (Ctrl+V)
- System extracts image data and stores
- Auto-detection of image name and metadata
- Google Drive and other cloud service images supported

**Unified Storage**
- All images stored in consistent media library
- Centralized folder assignment at site creation
- Auto-tagging with site association
- Metadata extraction (dimensions, format, file size)

### 5.3 Image Processing Pipeline

**Format Conversion**
- Input: Any format (JPG, PNG, SVG, WebP, GIF)
- Output: Optimized for web delivery

**SVG Handling (for Logos/Favicons)**
- SVG → PNG (16x16, 32x32, 48x48 pixels)
- SVG → ICO (multiple sizes packed)
- SVG → Apple Touch Icon (180x180)
- SVG → Safari Pinned Tab (for Safari menu bar)
- Original SVG preserved as fallback

**Standard Image Processing**
- Resize to mobile-friendly dimensions (if Page Speed enabled)
- Mobile: 480px width (responsive scaling)
- Desktop: 800px width (responsive scaling)
- Format selection (WebP primary, PNG/JPEG fallback)
- Automatic srcset generation for responsive images

**Image Fingerprinting**
- Slight size variations per site (±1-3%)
- Different quality levels per site
- Random cropping option (minimal, preserves content)
- Metadata stripping (privacy, reduced file size)

---

## Part 6: Site Creation & Configuration Workflow

### 6.1 Step 1: Domain & Token Selection

**Domain Input**
- User enters domain name
- Validation: Check domain availability (optional API check)
- Format: domain.com (without protocol or trailing slash)

**Cloudflare Token Selection Modal**
- Display table with three columns:
  - Checkbox (for selection)
  - Token Name (human-readable label from settings)
  - Associated Sites (list of domains already using this token)
- Single token selection required
- Button: "Copy NS Records" (copy Cloudflare nameservers to clipboard)
- Button: "Continue Site Creation"

**Result**
- Cloudflare API call to create DNS zone
- NS records returned for domain registrar setup
- User instruction message (set NS records at registrar)

### 6.2 Step 2: Site Configuration

**Brand Settings**
- Brand Name: Text input (used in branding elements)
- Domain: Pre-filled from Step 1
- Language: Dropdown (from preset languages)
- Geo-targeting: Optional (for regional optimization)

**Affiliate Settings**
- Affiliate Link: Dropdown (select from preset links in settings)
- Link applies to all CTA buttons automatically

**Template Selection**
- Template: Dropdown (list all uploaded templates)
- Fingerprint Type: Dropdown selection
  - Option 1: Random class name generation
  - Option 2: Select from preset class naming schemes
  - Option 3: WordPress footprint (special path structure)
  - Option 4: Other CMS footprints

**SEO Settings**
- Checkbox: "Allow Search Engine Indexing" (default: checked)
  - Checked: No noindex tag
  - Unchecked: Add `<meta name="robots" content="noindex">`

**Cloudflare Rules**
- Checkbox: "Redirect 404 to Homepage" (default: unchecked)
  - Creates Cloudflare Rule with specific filter expression
  - Excludes static assets and API routes from redirect
  
- Checkbox: "Force WWW Version" (default: unchecked)
  - Creates Cloudflare redirect rule: www → non-www (301)
  - Alternative: non-www → www (if preferred)

**Icon Configuration**
- Favicon Upload: SVG format (required)
  - Selection from media library or direct upload
  - System generates all required sizes and formats
  - Generated outputs: favicon.ico, favicon.png (16x16, 32x32, 48x48), apple-touch-icon.png, favicon.svg
  
- Logo Upload: Any format preferred
  - Selection from media library or direct upload
  - Single source, applied throughout site
  - Formats: SVG or PNG recommended

**Page Structure Definition**
- Create page list for site
- Home page included by default (cannot delete)
- Each page entry: URL slug and Page Title (used in menu)
- Per-page display options:
  - Checkbox: Show in Header Menu
  - Checkbox: Show in Footer Menu
  - Checkbox: Show in Sidebar (if template supports)
- Default page links reappear if changed during page editing

**Footer Images Selection**
- Select images from media library (payment methods, providers, etc.)
- Optional substitution during site generation
- Default images can be overridden per site

**Header CTA Button Configuration**
- Number of buttons: 1 or 2 options
- Per button:
  - Button text (manual input)
  - Button color: Select from template colors (primary, accent, etc.)
  - Link: Automatically uses selected Affiliate Link
- Buttons appear in header area (based on template design)

**Page Speed Optimization** (Optional)
- Checkbox: "Enable Page Speed Optimization" (default: unchecked)
  - When enabled:
    - Convert all `<img>` tags to `<picture>` tags
    - Generate responsive image sets (mobile: 480px, desktop: 800px)
    - Automatic WebP conversion with fallbacks
    - Lazy loading attributes added
    - Image dimensions vary per site (±1-3%) for uniqueness

**Microdata/Structured Data**
- Inherit from system presets (checkbox)
- If unchecked: manually select which microdata to include
- Displayed microdata appears with variable placeholders pre-filled
- Custom microdata: paste JSON-LD or other markup
- Conditional display (only output if values exist)

**Custom Head HTML**
- Text area: paste custom HTML for `<head>` section
- Use case: custom meta tags, canonical alternates, verification tags
- Not implemented in initial release (noted for future)

### 6.3 Step 3: Site Creation & Page Initialization

**System Actions**
- Save all site configuration to database
- Create default home page (/index.html)
- Create all pages defined in page structure
- Initialize page settings with empty content
- Redirect user to Pages management view

**Not Deployed Yet**
- Site configuration saved but not deployed to Cloudflare
- No static files generated
- No deployment until user completes page content

---

## Part 7: Page Content Management

### 7.1 Page Editing Interface

**Navigation & Info**
- List of all site pages in table format
- Columns: ID, Slug, Title, Quick Actions (Edit, Duplicate, Delete)
- Display page creation date and last modified date
- "Delete Page" button (with confirmation)

### 7.2 SEO Fields

**Title**
- Meta title for page
- If empty, auto-generated via AI prompt on save
- Max: 60 characters (recommended)

**Meta Description**
- Meta description for page
- If empty, auto-generated via AI prompt on save
- Max: 160 characters (recommended)

**H1 Heading**
- Main page heading
- Checkbox: "Use H1 in Hero Block" (default: unchecked)
  - Checked: H1 renders as heading in hero block
  - Unchecked: H1 renders as regular paragraph styled as H1 in article block
- This prevents conflicting H1 tags across blocks
- If unchecked, H1 can be placed anywhere in article content

**Canonical URL**
- Auto-filled with site domain + page slug
- User can override for special cases (e.g., duplicate content management)
- Example: Homepage canonical to non-www version

**Custom Head HTML**
- Additional HTML code for page-specific head section
- Use case: alternate language links, verification codes
- Future implementation noted

### 7.3 Content Generation Metadata

**Keyword Input**
- Field: "Primary Keywords"
- Format: One keyword per line
- Used for AI content generation
- Example: "casino online", "best poker games"

**LSI Keywords**
- Field: "Latent Semantic Index Keywords"
- Format: One LSI phrase per line
- Used for AI content generation diversity
- Example: "gambling platforms", "online gaming sites"

**Generation Modal**
- When user clicks "Generate", modal appears
- Checklist: Select which blocks/fields to generate
- Dropdown per item: Select prompt to use (from preset prompts)
- Option: Use competitor data (URLs or copied titles)
- Advanced mode: Load competitor HTML and extract titles/descriptions
- Execute generation

---

## Part 8: Content Blocks System

### 8.1 Block Types

**Hero Block (Banner)**
- Image selection from media library
- Headline: Auto-populated from page H1 (if enabled)
- Subheading: Optional CTA text
- CTA Buttons: 1-2 buttons with custom text
- Button links: Use affiliate link + optional tracking params
- Styling: Template colors and typography

**Article Block**
- Rich text editor with three modes:
  - Constructor mode (WYSIWYG builder)
  - HTML mode (raw HTML editing)
  - Markdown mode (markdown input)
  - Live preview of output
- Open Article Tag: Checkbox to wrap content in `<article>` tag
- Close Article Tag: Checkbox to close article tag
- Rationale: Multiple blocks can be wrapped in single article tag
- Text formatting:
  - Font size control
  - Bold, italic, underline
  - Heading styles (H2, H3, H4)
  - Block quotes
  - Code blocks
  - Lists (ordered, unordered)
  - Column layouts (1, 2, 3 columns)
  - Hyperlinks with custom text
- Empty article: Auto-generated if not filled
- Accessible markdown import: Auto-convert markdown to HTML

**Image Block**
- Single image display
- Image selection: Browse media library by folder
- Dimensions: Maintain aspect ratio or custom sizing
- Alt text: Per-site customization
- Title attribute: Per-site customization
- Lazy loading: Automatic

**Text + Image Block**
- Text content (left or right)
- Image positioning: Left/Right toggle
- Text: Same formatting as article block
- Image: Same options as image block
- Responsive: Stack on mobile, side-by-side on desktop

**Call-to-Action Block**
- Multiple CTA buttons
- Per button:
  - Text input
  - Link (auto-filled affiliate link or custom URL)
  - Color selection (primary, secondary, accent)
  - Size: Small, medium, large
- Layout options: Horizontal or vertical stacking

**FAQ Block**
- Question/Answer pairs
- Each item: Question and Answer fields
- Answer supports text formatting (same as article block)
- UI: Accordion or expandable list
- "Add Item" button to add new Q&A pairs
- Block title: Configurable
- Empty block: Auto-generated if not filled
- Generation: Can be AI-generated based on keywords

**Swiper/Carousel Block**
- Display games or product carousel
- Per item:
  - Image (from media library)
  - Game/Product name
  - CTA Button with custom text (shared across all items)
- Navigation: Previous/Next buttons or dots
- Auto-scroll: Optional with interval setting

**Swiper Presets**
- Admin can create preset carousels
- Each preset:
  - Preset name
  - List of images with per-image names
  - Shared button text
- Users select preset instead of manually adding items
- Saves time for repeated carousel configurations

### 8.2 Block Management

**Adding Blocks**
- Button: "Add Block" in page editor
- Modal: Select block type from available options
- Block appends to page (or at specified position)
- Each block assigned unique ID for reference

**Block Operations**
- Edit: Click to expand and modify block content
- Duplicate: Copy block with all settings
- Delete: Remove block from page
- Reorder: Drag-and-drop or arrow buttons

**Block Visibility States**
- Empty/Not filled: System indicates content needed
- Auto-generation ready: Can trigger AI generation
- Complete: All required fields filled
- Optional fields: Can be left blank

---

## Part 9: AI Content Generation

### 9.1 Generation Workflow

**Trigger Generation**
- User clicks "Generate" button (per block or full page)
- Modal appears: Checklist of blocks/fields ready for generation
- Selection: Choose which items to generate
- Prompt selection: Dropdown per item (select from preset prompts)

**Generation Modal Options**

**Simple Generation**
- Select block type (Title, Description, Article, FAQ)
- Select prompt from presets
- Click "Generate"
- System sends request to AI with:
  - Page keywords
  - LSI phrases
  - Selected prompt content
  - Brand name
  - Site language

**Advanced Generation (Future)**
- Option: Load competitor URLs
- Extract competitor titles/descriptions
- Include in generation context
- System prompt: "Generate similar but better content based on these competitors"

**Generation Result**
- Content appears in modal preview
- User can accept or regenerate
- Regenerate: Same prompt or different prompt
- Apply: Content fills the block/field

### 9.2 Prompt Configuration

**Prompt Definition Fields**
- Prompt Name: User-friendly label
- Content Type: article/title/description/FAQ/hero
- AI Model: ChatGPT (GPT-4, GPT-3.5) or Grok
- Temperature: 0-1 slider (0=deterministic, 1=creative)
- Prompt Text: Full instruction with variable placeholders
- Output Format: HTML/Markdown/Plain text

**Available Variables in Prompts**
- `{{keywords}}` - Primary keywords for page
- `{{lsi_phrases}}` - LSI keywords for page
- `{{brand}}` - Site brand name
- `{{language}}` - Page language
- `{{tone}}` - Brand voice (formal, casual, expert)
- `{{context}}` - Custom context provided by user

### 9.3 Generation Quality & Regeneration

**Regeneration Policy**
- User can regenerate any block multiple times
- Each generation uses selected prompt
- Different prompts yield different outputs
- Temperature affects consistency (lower = more consistent)

**Generation Limits** (Optional)
- Admin can set daily generation limits per user
- Track API usage and costs
- Prevent abuse of AI services

---

## Part 10: Page Save & Preview

### 10.1 Save Functionality

**Save Button**
- Located: Top right of page editor
- Action: Save all page content to database
- Validation: Check for required fields
- Database update: All blocks, text, metadata

**Auto-save** (Optional)
- Periodically save changes
- Indicator: "Saving..." notification
- Conflict resolution: Last edit wins

### 10.2 Preview Functionality

**Preview Generation**
- Button: "Preview Site"
- System renders full page as it would appear on live site
- Includes: Styling, images, layout, responsive preview
- Mobile view: 480px width
- Desktop view: 800px width
- Toggle between views

**Preview Features**
- Read-only rendering
- Interactive links (affiliate links functional)
- Form display (if present)
- Analytics script preview (not functional, display only)

**Real-time Preview** (Optional with WebSocket)
- Live update as content changes
- Send content to backend preview generator
- Display in side panel
- Requires: Django Channels setup

---

## Part 11: Site Deployment

### 11.1 Deployment Process

**Pre-deployment Checks**
- All pages have content
- Required fields filled
- Images processed and optimized
- No broken links
- CSS/JS properly fingerprinted

**Deployment Steps**

**Step 1: Static Site Generation**
- Generate all HTML files per page
- Apply all template variables
- Substitute brand, domain, content
- Generate complete file structure
- Apply fingerprinting (random classes or preset scheme)
- Process all images:
  - Apply format conversions (WebP, PNG)
  - Generate responsive sizes
  - Apply page speed optimizations if enabled
- Output: ZIP file with complete site structure

**Step 2: Asset Processing**
- Generate all favicon variants from SVG
- Copy/optimize all images
- Compile CSS (with fingerprinted class names)
- Compile JavaScript (with proper async loading)
- Generate sitemap.xml
- Generate robots.txt (respecting noindex setting)

**Step 3: Cloudflare Pages Deployment**
- Authenticate with Cloudflare API using stored token
- Delete previous deployment (all old files)
- Upload new files to Cloudflare Pages
- Upload complete new site (no incremental updates)
- Configure Cloudflare rules:
  - 404 redirect (if enabled)
  - WWW redirect (if enabled)
  - Header rules (cache control, security headers)
  - Page rules (custom domain, SSL)

**Step 4: DNS & Domain Setup**
- Verify domain NS records point to Cloudflare
- Configure domain routing
- Set SSL certificate (automatic via Cloudflare)
- Activate domain

**Step 5: Analytics Integration**
- Inject Umami analytics script into all pages
- Configure tracking: Site ID, domain
- Verify tracking activation

**Deployment Result**
- Site live at configured domain
- All pages accessible
- Analytics tracking active
- Deployment logged in history

### 11.2 Deployment Management

**Deployment History**
- Table: All previous deployments
- Columns: Date/Time, Status, Files deployed, Deployment size
- Button: "Rollback to Previous" (restore previous version)
- Download backup: ZIP archive of deployed version

**Download Site**
- Alternative to deploying: Download generated site as ZIP
- Use case: Local testing, deployment to other platforms
- File: Complete site structure ready for upload
- Includes: All assets, images, optimized files

---

## Part 12: Analytics Dashboard

### 12.1 Analytics Integration

**Umami Integration**
- Track page views, unique visitors, referrers
- Browser/OS statistics
- Device breakdown (mobile, desktop)
- Geographic data (if configured)
- Time-based analytics

**Dashboard Display**
- Sidebar menu: "Analytics" option
- Page-level view: Analytics for individual pages
- Site-level view: Aggregate analytics across all pages
- Time period selection: Today, last 7 days, last 30 days, custom range

**Analytics Widgets**
- Total page views
- Unique visitors (this period vs. previous)
- Top pages
- Traffic sources (referrers)
- Device/Browser breakdown
- Geographic distribution
- Bounce rate
- Average session duration

### 12.2 Analytics Features

**Reporting**
- Export analytics to CSV/PDF
- Custom date range selection
- Comparison: This period vs. previous period
- Trend graphs (line charts for time-series data)

**Alerts** (Optional)
- Alert on high traffic
- Alert on traffic drops
- Alert on unusual geographic spikes

---

## Part 13: Admin Panel Features

### 13.1 Dashboard Main Page

**Site List**
- Table displaying all sites
- Columns: Domain, Brand, Language, Geo, Created Date, Last Modified, Status
- Filters:
  - By Language
  - By Brand
  - By Geo-targeting
  - By Status (active, inactive, draft)
  - Search: Domain name search
- Quick actions per site:
  - Edit: Open site configuration
  - Duplicate: Create copy of site with all pages
  - Delete: Remove site and all associated data
  - View Analytics: Open analytics dashboard
  - Download: Get current deployment as ZIP
  - Deploy: Trigger deployment to Cloudflare

**Dashboard Cards**
- Total sites (count)
- Sites deployed (count)
- Total pages (across all sites)
- Storage used (MB)
- API quota remaining

### 13.2 Site-Level Dashboard

**Nested Navigation**
- Click site in list → Site-specific dashboard
- Tabs: Settings, Pages, Analytics, Deployments

**Settings Tab**
- All configuration from creation
- Editable fields (all except domain)
- Update button to save changes

**Pages Tab**
- List of all pages for site
- Quick actions: Edit, Duplicate, Delete
- "Add Page" button

**Analytics Tab**
- Umami analytics embedded
- Site-specific metrics

**Deployments Tab**
- Deployment history
- Current deployed version
- Rollback options
- Download backup

---

## Part 14: Sidebar Navigation

### 14.1 Sidebar Menu Options

**Dashboard** (Home)
- Main site list view
- Quick stats

**Media Library**
- Browse all media files
- Folder structureT
- Upload new images
- Organize and manage files
- Preview images
- Delete files/folders

**Analytics** (Global)
- Cross-site analytics
- Compare multiple sites
- Admin-only detailed reporting

**Settings** (Admin)
- Global system settings
- Language presets
- API tokens
- Affiliate links
- Microdata presets

**Prompts** (Admin)
- Text generation prompts
- Image generation prompts
- CRUD operations on prompts

**Templates** (Admin)
- List all templates
- Upload new template
- Edit existing template
- Delete template
- Set as default

**Sites** (Technical)
- Alternative view of all sites
- Bulk operations
- Admin-only detailed view

---
