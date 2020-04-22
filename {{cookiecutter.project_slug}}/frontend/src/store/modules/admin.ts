import { api } from "@/api";
import { VuexModule, Module, Mutation, Action } from "vuex-module-decorators";
import { IUserProfile, IUserProfileUpdate, IUserProfileCreate } from "@/interfaces";
import { mainStore } from "@/utils/store-accessor";

@Module({ name: "admin" })
export default class AdminModule extends VuexModule {
  users: IUserProfile[] = [];

  get adminOneUser() {
    return (userId: number) => {
      const filteredUsers = this.users.filter((user) => user.id === userId);
      if (filteredUsers.length > 0) {
        return { ...filteredUsers[0] };
      }
    };
  }

  @Mutation
  setUsers(payload: IUserProfile[]) {
    this.users = payload;
  }

  @Mutation
  setUser(payload: IUserProfile) {
    const users = this.users.filter((user: IUserProfile) => user.id !== payload.id);
    users.push(payload);
    this.users = users;
  }

  @Action
  async getUsers() {
    try {
      const response = await api.getUsers(mainStore.token);
      if (response) {
        this.setUsers(response.data);
      }
    } catch (error) {
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async updateUser(payload: { id: number; user: IUserProfileUpdate }) {
    try {
      const loadingNotification = { content: "saving", showProgress: true };
      mainStore.addNotification(loadingNotification);
      const response = (
        await Promise.all([
          api.updateUser(mainStore.token, payload.id, payload.user),
          await new Promise((resolve, _reject) => setTimeout(() => resolve(), 500)),
        ])
      )[0];
      mainStore.setUserProfile(response.data);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "User successfully updated",
        color: "success",
      });
    } catch (error) {
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async createUser(payload: IUserProfileCreate) {
    try {
      const loadingNotification = { content: "saving", showProgress: true };
      mainStore.addNotification(loadingNotification);
      await Promise.all([
        api.createUser(mainStore.token, payload),
        await new Promise((resolve, _reject) => setTimeout(() => resolve(), 500)),
      ]);
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "User successfully created",
        color: "success",
      });
    } catch (error) {
      await mainStore.checkApiError(error);
    }
  }
}
