import { createLocalVue, mount } from "@vue/test-utils";
import Login from "@/views/Login.vue";
import "@/plugins/vuetify";
import VueRouter from "vue-router";
import Vuetify from "vuetify";
import { componentWithText } from "../utils";

import Vuex, { ActionTree, GetterTree, Store } from "vuex";

const localVue = createLocalVue();

localVue.use(VueRouter);
const router = new VueRouter();

localVue.use(Vuex);

describe("Login.vue", () => {
  /* eslint-disable @typescript-eslint/no-explicit-any */
  let getters: GetterTree<any, any>;
  let actions: ActionTree<any, any>;
  let store: Store<any>;
  /* eslint-enable @typescript-eslint/no-explicit-any */
  let vuetify;

  beforeEach(() => {
    vuetify = new Vuetify();
    getters = {};

    actions = {
      actionLogIn: jest.fn(),
    };

    store = new Vuex.Store({
      getters,
      actions,
    });
  });

  it("calls the login action", async () => {
    const wrapper = mount(Login, { store, localVue, router, vuetify });
    const textFields = wrapper.findAllComponents({ name: "v-text-field" });
    const emailField = componentWithText(textFields, "Login");
    emailField.get("input").setValue("yo@da.com");
    const passwordField = componentWithText(textFields, "Password");
    passwordField.get("input").setValue("secretpass");

    const loginBtn = componentWithText(
      wrapper.findAllComponents({ name: "v-btn" }),
      "Login",
    );
    loginBtn.trigger("click");

    expect(actions.actionLogIn).toHaveBeenCalledWith(expect.anything(), {
      username: "yo@da.com",
      password: "secretpass",
    });
  });
});
