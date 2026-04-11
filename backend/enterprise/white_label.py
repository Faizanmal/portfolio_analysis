"""
White-Label Platform Customization
===================================

Complete white-label solution for enterprise clients:
- Custom branding and theming
- Logo and color customization
- Custom domain support
- Client-specific feature toggles
- White-labeled reports and exports
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging
import hashlib


class ThemeMode(Enum):
    """Theme modes"""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class FontFamily(Enum):
    """Available font families"""
    INTER = "Inter"
    ROBOTO = "Roboto"
    OPEN_SANS = "Open Sans"
    LATO = "Lato"
    POPPINS = "Poppins"
    MONTSERRAT = "Montserrat"
    SOURCE_SANS = "Source Sans Pro"


@dataclass
class ColorPalette:
    """Color palette for branding"""
    primary: str = "#1a73e8"
    primary_dark: str = "#1557b0"
    primary_light: str = "#4285f4"
    secondary: str = "#34a853"
    accent: str = "#fbbc04"
    error: str = "#ea4335"
    warning: str = "#ff9800"
    success: str = "#34a853"
    info: str = "#2196f3"
    
    # Neutrals
    background: str = "#ffffff"
    surface: str = "#f8f9fa"
    text_primary: str = "#202124"
    text_secondary: str = "#5f6368"
    border: str = "#dadce0"
    
    # Chart colors
    chart_colors: List[str] = field(default_factory=lambda: [
        "#1a73e8", "#34a853", "#fbbc04", "#ea4335", 
        "#9334e8", "#ff6d00", "#00897b", "#5c6bc0"
    ])
    
    def to_css_variables(self) -> str:
        """Generate CSS custom properties"""
        css = ":root {\n"
        css += f"  --color-primary: {self.primary};\n"
        css += f"  --color-primary-dark: {self.primary_dark};\n"
        css += f"  --color-primary-light: {self.primary_light};\n"
        css += f"  --color-secondary: {self.secondary};\n"
        css += f"  --color-accent: {self.accent};\n"
        css += f"  --color-error: {self.error};\n"
        css += f"  --color-warning: {self.warning};\n"
        css += f"  --color-success: {self.success};\n"
        css += f"  --color-info: {self.info};\n"
        css += f"  --color-background: {self.background};\n"
        css += f"  --color-surface: {self.surface};\n"
        css += f"  --color-text-primary: {self.text_primary};\n"
        css += f"  --color-text-secondary: {self.text_secondary};\n"
        css += f"  --color-border: {self.border};\n"
        for i, color in enumerate(self.chart_colors):
            css += f"  --chart-color-{i+1}: {color};\n"
        css += "}\n"
        return css


@dataclass
class BrandingConfig:
    """Complete branding configuration"""
    # Identity
    company_name: str = "Portfolio Analytics"
    product_name: str = "Portfolio Pro"
    tagline: str = "Intelligent Investment Management"
    
    # Logo
    logo_url: str = ""
    logo_dark_url: str = ""  # For dark mode
    favicon_url: str = ""
    logo_width: int = 150
    logo_height: int = 40
    
    # Colors
    colors: ColorPalette = field(default_factory=ColorPalette)
    
    # Typography
    font_family: FontFamily = FontFamily.INTER
    heading_font: FontFamily = FontFamily.INTER
    font_size_base: int = 14
    
    # Custom domain
    custom_domain: str = ""
    subdomain: str = ""
    
    # Contact
    support_email: str = ""
    support_phone: str = ""
    website_url: str = ""
    
    # Legal
    terms_url: str = ""
    privacy_url: str = ""
    copyright_text: str = ""
    
    # Social
    linkedin_url: str = ""
    twitter_url: str = ""
    
    # Feature toggles
    show_powered_by: bool = True
    enable_dark_mode: bool = True
    enable_notifications: bool = True
    
    def get_copyright(self) -> str:
        """Get copyright text"""
        if self.copyright_text:
            return self.copyright_text
        year = datetime.now().year
        return f"© {year} {self.company_name}. All rights reserved."
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'company_name': self.company_name,
            'product_name': self.product_name,
            'tagline': self.tagline,
            'logo_url': self.logo_url,
            'colors': {
                'primary': self.colors.primary,
                'secondary': self.colors.secondary,
                'accent': self.colors.accent
            },
            'font_family': self.font_family.value,
            'custom_domain': self.custom_domain,
            'support_email': self.support_email,
            'copyright': self.get_copyright()
        }


class ThemeManager:
    """
    Manages themes and styling for white-label clients.
    """
    
    def __init__(self, storage_path: str = "./themes"):
        self.logger = logging.getLogger("theme_manager")
        self.storage_path = storage_path
        self.themes: Dict[str, Dict[str, Any]] = {}
        self._load_default_themes()
    
    def _load_default_themes(self):
        """Load default themes"""
        # Light theme
        self.themes['light'] = {
            'name': 'Light',
            'mode': ThemeMode.LIGHT.value,
            'colors': ColorPalette().to_css_variables(),
            'is_default': True
        }
        
        # Dark theme
        dark_palette = ColorPalette(
            background="#1a1a2e",
            surface="#16213e",
            text_primary="#eaeaea",
            text_secondary="#a0a0a0",
            border="#2a2a4e"
        )
        self.themes['dark'] = {
            'name': 'Dark',
            'mode': ThemeMode.DARK.value,
            'colors': dark_palette.to_css_variables(),
            'is_default': False
        }
    
    def create_custom_theme(
        self,
        theme_id: str,
        name: str,
        palette: ColorPalette,
        mode: ThemeMode = ThemeMode.LIGHT
    ) -> str:
        """Create a custom theme"""
        self.themes[theme_id] = {
            'name': name,
            'mode': mode.value,
            'colors': palette.to_css_variables(),
            'is_default': False,
            'created_at': datetime.now().isoformat()
        }
        self.logger.info(f"Created custom theme: {name}")
        return theme_id
    
    def get_theme(self, theme_id: str) -> Optional[Dict[str, Any]]:
        """Get theme by ID"""
        return self.themes.get(theme_id)
    
    def generate_css(self, branding: BrandingConfig) -> str:
        """Generate complete CSS from branding config"""
        css = branding.colors.to_css_variables()
        
        # Add typography
        css += f"""
body {{
    font-family: '{branding.font_family.value}', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: {branding.font_size_base}px;
    color: var(--color-text-primary);
    background-color: var(--color-background);
}}

h1, h2, h3, h4, h5, h6 {{
    font-family: '{branding.heading_font.value}', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: var(--color-text-primary);
}}

.btn-primary {{
    background-color: var(--color-primary);
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    cursor: pointer;
    transition: background-color 0.2s;
}}

.btn-primary:hover {{
    background-color: var(--color-primary-dark);
}}

.card {{
    background-color: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 8px;
    padding: 16px;
}}

.text-secondary {{
    color: var(--color-text-secondary);
}}
"""
        return css


class WhiteLabelPlatform:
    """
    Complete white-label platform management.
    """
    
    def __init__(self, config_path: str = "./config/white_label"):
        self.logger = logging.getLogger("white_label")
        self.config_path = config_path
        self.theme_manager = ThemeManager()
        self.clients: Dict[str, BrandingConfig] = {}
        self.feature_flags: Dict[str, Dict[str, bool]] = {}
    
    def register_client(
        self,
        client_id: str,
        branding: BrandingConfig,
        features: Optional[Dict[str, bool]] = None
    ) -> str:
        """Register a new white-label client"""
        self.clients[client_id] = branding
        
        # Default features
        default_features = {
            'portfolio_analytics': True,
            'risk_management': True,
            'trading': True,
            'reporting': True,
            'ai_insights': True,
            'multi_asset': False,
            'api_access': False,
            'custom_reports': False,
            'white_label_exports': False,
            'dedicated_support': False
        }
        
        if features:
            default_features.update(features)
        
        self.feature_flags[client_id] = default_features
        
        self.logger.info(f"Registered white-label client: {branding.company_name}")
        return client_id
    
    def get_client_branding(self, client_id: str) -> Optional[BrandingConfig]:
        """Get branding config for client"""
        return self.clients.get(client_id)
    
    def update_branding(
        self,
        client_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update client branding"""
        if client_id not in self.clients:
            return False
        
        branding = self.clients[client_id]
        
        for key, value in updates.items():
            if hasattr(branding, key):
                setattr(branding, key, value)
        
        self.logger.info(f"Updated branding for client: {client_id}")
        return True
    
    def is_feature_enabled(
        self,
        client_id: str,
        feature: str
    ) -> bool:
        """Check if feature is enabled for client"""
        client_features = self.feature_flags.get(client_id, {})
        return client_features.get(feature, False)
    
    def toggle_feature(
        self,
        client_id: str,
        feature: str,
        enabled: bool
    ):
        """Toggle a feature for client"""
        if client_id not in self.feature_flags:
            self.feature_flags[client_id] = {}
        
        self.feature_flags[client_id][feature] = enabled
        self.logger.info(f"Feature '{feature}' set to {enabled} for client {client_id}")
    
    def generate_client_assets(
        self,
        client_id: str
    ) -> Dict[str, str]:
        """Generate all assets for a client"""
        branding = self.clients.get(client_id)
        if not branding:
            return {}
        
        # Generate CSS
        css = self.theme_manager.generate_css(branding)
        
        # Generate manifest for PWA
        manifest = {
            "name": branding.product_name,
            "short_name": branding.product_name[:12],
            "description": branding.tagline,
            "start_url": "/",
            "display": "standalone",
            "theme_color": branding.colors.primary,
            "background_color": branding.colors.background,
            "icons": [
                {"src": branding.favicon_url, "sizes": "192x192", "type": "image/png"}
            ] if branding.favicon_url else []
        }
        
        # Generate email template header
        email_header = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: {branding.font_family.value}, sans-serif; }}
        .header {{ background-color: {branding.colors.primary}; padding: 20px; }}
        .logo {{ max-width: {branding.logo_width}px; }}
    </style>
</head>
<body>
    <div class="header">
        <img src="{branding.logo_url}" alt="{branding.company_name}" class="logo">
    </div>
    <div class="content">
"""
        
        return {
            'css': css,
            'manifest': json.dumps(manifest, indent=2),
            'email_header': email_header
        }
    
    def generate_report_header(
        self,
        client_id: str
    ) -> str:
        """Generate HTML header for reports"""
        branding = self.clients.get(client_id)
        if not branding:
            return ""
        
        return f"""
<div style="
    display: flex; 
    justify-content: space-between; 
    align-items: center;
    padding: 20px;
    border-bottom: 2px solid {branding.colors.primary};
    margin-bottom: 30px;
">
    <div>
        <img src="{branding.logo_url}" 
             alt="{branding.company_name}" 
             style="max-height: {branding.logo_height}px;">
    </div>
    <div style="text-align: right;">
        <div style="font-size: 12px; color: {branding.colors.text_secondary};">
            {branding.tagline}
        </div>
    </div>
</div>
"""
    
    def generate_report_footer(
        self,
        client_id: str
    ) -> str:
        """Generate HTML footer for reports"""
        branding = self.clients.get(client_id)
        if not branding:
            return ""
        
        footer = f"""
<div style="
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid {branding.colors.border};
    font-size: 11px;
    color: {branding.colors.text_secondary};
    text-align: center;
">
    <div>{branding.get_copyright()}</div>
"""
        
        if branding.support_email:
            footer += f'    <div>Contact: {branding.support_email}</div>\n'
        
        if branding.website_url:
            footer += f'    <div><a href="{branding.website_url}">{branding.website_url}</a></div>\n'
        
        if branding.show_powered_by:
            footer += '    <div style="margin-top: 10px; font-style: italic;">Powered by Portfolio Analytics Platform</div>\n'
        
        footer += "</div>"
        
        return footer
    
    def get_domain_config(
        self,
        client_id: str
    ) -> Dict[str, Any]:
        """Get custom domain configuration"""
        branding = self.clients.get(client_id)
        if not branding:
            return {}
        
        return {
            'custom_domain': branding.custom_domain,
            'subdomain': branding.subdomain,
            'ssl_required': True,
            'cname_target': 'platform.portfolio-analytics.com',
            'dns_records': [
                {'type': 'CNAME', 'name': branding.subdomain or 'www', 'value': 'platform.portfolio-analytics.com'},
                {'type': 'TXT', 'name': '_verify', 'value': f'pa-verify={hashlib.md5(client_id.encode()).hexdigest()[:16]}'}
            ]
        }
