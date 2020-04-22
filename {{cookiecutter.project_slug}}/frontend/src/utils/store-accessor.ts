import { Store } from "vuex";
import { getModule } from "vuex-module-decorators";
import MainModule from "@/store/modules/main";
import AdminModule from "@/store/modules/admin";

let mainStore: MainModule;
let adminStore: AdminModule;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function initializeStores(store: Store<any>): void {
  mainStore = getModule(MainModule, store);
  adminStore = getModule(AdminModule, store);
}

export const modules = {
  main: MainModule,
  admin: AdminModule,
};

export { initializeStores, mainStore, adminStore };
