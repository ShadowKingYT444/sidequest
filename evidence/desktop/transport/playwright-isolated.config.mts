// Read-only protocol-fake UI checks can run apart from a frozen office suite.
import {defineConfig} from '../../../desktop/node_modules/@playwright/test/index.mjs';
import base from '../../../desktop/playwright.config.ts';
const desktopRoot=new URL('../../../desktop/',import.meta.url).pathname;
export default defineConfig({...base,testDir:desktopRoot+'tests/browser',use:{...base.use,baseURL:'http://127.0.0.1:5175'},webServer:{command:'npm run dev -- --port 5175',cwd:desktopRoot,url:'http://127.0.0.1:5175',reuseExistingServer:false,timeout:30000}});
