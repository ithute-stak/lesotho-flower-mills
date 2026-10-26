import {defineConfig} from "@playwright/test";
export default defineConfig({
 testDir:"./tests",timeout:30000,retries:1,workers:1,
 use:{headless:true,trace:"retain-on-failure"},
 webServer:[
  {command:"npm run dev -- --port 3100",cwd:"../apps/customer-web",url:"http://127.0.0.1:3100",reuseExistingServer:!process.env.CI,timeout:120000},
  {command:"npm run dev -- --port 3101",cwd:"../apps/admin-web",url:"http://127.0.0.1:3101",reuseExistingServer:!process.env.CI,timeout:120000},
  {command:"npm run dev -- --port 3102",cwd:"../apps/warehouse-web",url:"http://127.0.0.1:3102",reuseExistingServer:!process.env.CI,timeout:120000},
  {command:"npm run dev -- --port 3103",cwd:"../apps/driver-web",url:"http://127.0.0.1:3103",reuseExistingServer:!process.env.CI,timeout:120000}
 ]
});
