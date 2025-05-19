import os
import base64
from typing import Dict, Any, Optional, List, Tuple
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext, ElementHandle
from urllib.parse import urlparse, urljoin
import logging

logger = logging.getLogger(__name__)

class BrowserController:
    """Controls the browser automation using Playwright."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the browser controller.
        
        Args:
            config: System configuration
        """
        self.config = config
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.screenshot_counter = 0
        
    def start(self) -> None:
        """Start the browser session."""
        self.playwright = sync_playwright().start()
        
        # Choose browser
        browser_type = self.config.get("browser_type", "chromium")
        if browser_type == "firefox":
            browser_instance = self.playwright.firefox
        elif browser_type == "webkit":
            browser_instance = self.playwright.webkit
        else:
            browser_instance = self.playwright.chromium
        
        # Launch browser
        self.browser = browser_instance.launch(
            headless=self.config.get("headless", True)
        )
        
        # Create context with viewport
        self.context = self.browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        
        # Create page
        self.page = self.context.new_page()
        
        # Set timeout
        self.page.set_default_timeout(self.config.get("timeout", 30000))
        
        logger.info("Browser started")
    
    def stop(self) -> None:
        """Stop the browser session."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Browser stopped")
    
    def navigate(self, url: str) -> bool:
        """Navigate to a URL.
        
        Args:
            url: URL to navigate to
            
        Returns:
            True if navigation was successful, False otherwise
        """
        try:
            logger.info(f"Navigating to {url}")
            
            # Handle authentication if needed
            if self.config.get("auth_required") and not self._is_logged_in():
                if self._requires_login(url):
                    logger.info("Authentication required")
                    self._handle_authentication(url)
            
            response = self.page.goto(url, wait_until="networkidle")
            
            # Take screenshot if enabled
            if self.config.get("screenshot_on_step", True):
                self._take_screenshot(f"navigation_{self.screenshot_counter}")
                self.screenshot_counter += 1
            
            if not response:
                logger.warning(f"No response for navigation to {url}")
                return False
                
            return response.ok
            
        except Exception as e:
            logger.error(f"Navigation to {url} failed: {str(e)}")
            return False
    
    def click(self, selector: str, wait_for_navigation: bool = True) -> bool:
        """Click on an element.
        
        Args:
            selector: Element selector (CSS or XPath)
            wait_for_navigation: Whether to wait for navigation after click
            
        Returns:
            True if click was successful, False otherwise
        """
        try:
            logger.info(f"Clicking on {selector}")
            
            # Check if element exists and is visible
            if not self.page.locator(selector).is_visible():
                logger.warning(f"Element {selector} is not visible")
                return False
            
            if wait_for_navigation:
                with self.page.expect_navigation():
                    self.page.click(selector)
            else:
                self.page.click(selector)
            
            # Take screenshot if enabled
            if self.config.get("screenshot_on_step", True):
                self._take_screenshot(f"click_{self.screenshot_counter}")
                self.screenshot_counter += 1
                
            return True
            
        except Exception as e:
            logger.error(f"Click on {selector} failed: {str(e)}")
            return False
    
    def fill_form_field(self, selector: str, value: str) -> bool:
        """Fill a form field with a value.
        
        Args:
            selector: Element selector (CSS or XPath)
            value: Value to fill
            
        Returns:
            True if fill was successful, False otherwise
        """
        try:
            logger.info(f"Filling {selector} with value")
            
            # Check if element exists and is visible
            if not self.page.locator(selector).is_visible():
                logger.warning(f"Element {selector} is not visible")
                return False
            
            self.page.fill(selector, value)
            
            # Take screenshot if enabled
            if self.config.get("screenshot_on_step", True):
                self._take_screenshot(f"fill_{self.screenshot_counter}")
                self.screenshot_counter += 1
                
            return True
            
        except Exception as e:
            logger.error(f"Fill {selector} failed: {str(e)}")
            return False
    
    def select_option(self, selector: str, value: str) -> bool:
        """Select an option from a dropdown.
        
        Args:
            selector: Element selector (CSS or XPath)
            value: Value to select
            
        Returns:
            True if selection was successful, False otherwise
        """
        try:
            logger.info(f"Selecting option {value} in {selector}")
            
            # Check if element exists and is visible
            if not self.page.locator(selector).is_visible():
                logger.warning(f"Element {selector} is not visible")
                return False
            
            self.page.select_option(selector, value)
            
            # Take screenshot if enabled
            if self.config.get("screenshot_on_step", True):
                self._take_screenshot(f"select_{self.screenshot_counter}")
                self.screenshot_counter += 1
                
            return True
            
        except Exception as e:
            logger.error(f"Select option in {selector} failed: {str(e)}")
            return False
    
    def get_current_url(self) -> str:
        """Get the current URL.
        
        Returns:
            Current URL
        """
        return self.page.url
    
    def get_current_title(self) -> str:
        """Get the current page title.
        
        Returns:
            Current page title
        """
        return self.page.title()
    
    def get_dom_content(self) -> str:
        """Get the current page's DOM content.
        
        Returns:
            DOM content as HTML string
        """
        return self.page.content()
    
    def get_screenshot(self) -> str:
        """Get a screenshot of the current page as base64.
        
        Returns:
            Base64-encoded screenshot
        """
        screenshot_bytes = self.page.screenshot()
        return base64.b64encode(screenshot_bytes).decode('utf-8')
    
    def get_clickable_elements(self) -> List[Dict[str, Any]]:
        """Get all clickable elements on the page.
        
        Returns:
            List of element details
        """
        # Get all links
        links = self.page.query_selector_all('a[href]:not([href=""])')
        buttons = self.page.query_selector_all('button:not([disabled]), input[type="submit"]:not([disabled]), input[type="button"]:not([disabled])')
        
        elements = []
        
        # Process links
        for link in links:
            if not link.is_visible():
                continue
                
            href = link.get_attribute('href')
            text = link.inner_text().strip()
            
            if not text and link.query_selector('img'):
                # Link with image
                alt = link.query_selector('img').get_attribute('alt')
                text = f"Image link: {alt}" if alt else "Image link"
            
            elements.append({
                'type': 'link',
                'text': text or 'No text',
                'href': href,
                'selector': self._generate_selector(link)
            })
        
        # Process buttons
        for button in buttons:
            if not button.is_visible():
                continue
                
            text = button.inner_text().strip()
            if not text:
                text = button.get_attribute('value') or button.get_attribute('aria-label') or 'No text'
            
            elements.append({
                'type': 'button',
                'text': text,
                'selector': self._generate_selector(button)
            })
        
        return elements
    
    def get_form_elements(self) -> List[Dict[str, Any]]:
        """Get all form elements on the page.
        
        Returns:
            List of form element details
        """
        # Select common form elements
        selectors = [
            'input:not([type="hidden"])',
            'select',
            'textarea',
            'button[type="submit"]',
            'input[type="submit"]'
        ]
        
        form_elements = []
        
        # Find all forms
        forms = self.page.query_selector_all('form')
        form_count = len(forms)
        
        # If no forms, look for elements outside forms
        if form_count == 0:
            for selector in selectors:
                elements = self.page.query_selector_all(selector)
                for element in elements:
                    if element.is_visible():
                        form_elements.append(self._process_form_element(element, None))
        else:
            # Process elements within forms
            for i, form in enumerate(forms):
                form_id = form.get_attribute('id') or form.get_attribute('name') or f"form_{i+1}"
                elements = form.query_selector_all(', '.join(selectors))
                
                for element in elements:
                    if element.is_visible():
                        form_elements.append(self._process_form_element(element, form_id))
        
        return form_elements
    
    def _process_form_element(self, element: ElementHandle, form_id: Optional[str]) -> Dict[str, Any]:
        """Process a form element to extract its details.
        
        Args:
            element: Element handle
            form_id: ID of the form containing the element
            
        Returns:
            Element details
        """
        element_type = element.get_attribute('type') or element.tag_name().lower()
        element_id = element.get_attribute('id')
        element_name = element.get_attribute('name')
        
        # Find label text
        label_text = None
        if element_id:
            label = self.page.query_selector(f'label[for="{element_id}"]')
            if label:
                label_text = label.inner_text().strip()
        
        # If no explicit label, try nearby text or placeholder
        if not label_text:
            label_text = element.get_attribute('placeholder') or element.get_attribute('aria-label')
        
        # For buttons/submits, use their text or value
        if element_type in ['button', 'submit']:
            label_text = element.inner_text().strip() or element.get_attribute('value') or 'Submit'
        
        # Check if required
        required = element.get_attribute('required') is not None or element.get_attribute('aria-required') == 'true'
        
        return {
            'type': element_type,
            'id': element_id,
            'name': element_name,
            'form': form_id,
            'label': label_text or f"Unlabeled {element_type}",
            'required': required,
            'selector': self._generate_selector(element)
        }
    
    def _generate_selector(self, element: ElementHandle) -> str:
        """Generate a robust selector for an element.
        
        Args:
            element: Element handle
            
        Returns:
            CSS or XPath selector
        """
        # Try ID first (most reliable)
        element_id = element.get_attribute('id')
        if element_id:
            return f"#{element_id}"
        
        # Try name attribute
        element_name = element.get_attribute('name')
        if element_name:
            return f"[name='{element_name}']"
        
        # Try data attributes
        for attr in element.evaluate('elem => Object.keys(elem.dataset)'):
            value = element.get_attribute(f'data-{attr}')
            if value:
                return f"[data-{attr}='{value}']"
        
        # For buttons and links, try text content
        tag_name = element.tag_name().lower()
        if tag_name in ['button', 'a']:
            text = element.inner_text().strip()
            if text:
                # Create a text-based XPath
                return f"//{tag_name}[contains(text(), '{text}')]"
        
        # Fallback to a position-based selector (less reliable)
        return element.evaluate('elem => window.getComputedStyle(elem)')
    
    def _take_screenshot(self, name: str) -> str:
        """Take a screenshot and save it.
        
        Args:
            name: Screenshot name
            
        Returns:
            Path to the screenshot
        """
        output_dir = os.path.join(self.config.get("output_dir", "outputs"), "screenshots")
        os.makedirs(output_dir, exist_ok=True)
        
        path = os.path.join(output_dir, f"{name}.png")
        self.page.screenshot(path=path, full_page=True)
        return path
    
    def _handle_authentication(self, url: str) -> bool:
        """Handle authentication based on configuration.
        
        Args:
            url: Current URL
            
        Returns:
            True if authentication successful, False otherwise
        """
        auth_type = self.config.get("auth_type", "basic")
        
        if auth_type == "basic":
            # HTTP Basic Authentication
            username = self.config.get("auth_username", "")
            password = self.config.get("auth_password", "")
            
            parsed_url = urlparse(url)
            auth_url = f"{parsed_url.scheme}://{username}:{password}@{parsed_url.netloc}{parsed_url.path}"
            
            return self.navigate(auth_url)
            
        elif auth_type == "form":
            # Form-based login
            login_url = self.config.get("login_url", url)
            username_selector = self.config.get("username_selector", 'input[type="text"], input[name="username"], input[name="email"]')
            password_selector = self.config.get("password_selector", 'input[type="password"]')
            submit_selector = self.config.get("submit_selector", 'button[type="submit"], input[type="submit"]')
            
            # Navigate to login page
            self.navigate(login_url)
            
            # Fill username
            self.fill_form_field(username_selector, self.config.get("auth_username", ""))
            
            # Fill password
            self.fill_form_field(password_selector, self.config.get("auth_password", ""))
            
            # Click submit button
            return self.click(submit_selector)
            
        elif auth_type == "sso":
            # SSO login (basic implementation, may need customization)
            logger.info("SSO authentication not fully implemented")
            # This would need to be customized based on the specific SSO provider
            return False
            
        return False
    
    def _requires_login(self, url: str) -> bool:
        """Check if a URL requires login.
        
        Args:
            url: URL to check
            
        Returns:
            True if login required, False otherwise
        """
        # This is a simplistic check, might need enhancement
        # based on the specific application
        if self.config.get("login_detection_text"):
            detection_text = self.config.get("login_detection_text")
            self.navigate(url)
            return detection_text in self.page.content()
        
        return True  # Assume login required if not specified
    
    def _is_logged_in(self) -> bool:
        """Check if already logged in.
        
        Returns:
            True if logged in, False otherwise
        """
        # This would need to be customized based on the application
        if self.config.get("logged_in_detection_text"):
            detection_text = self.config.get("logged_in_detection_text")
            return detection_text in self.page.content()
        
        return False  # Assume not logged in if not specified
