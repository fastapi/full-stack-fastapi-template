import { useMutation } from "@tanstack/react-query";
import { UsersService } from "@/client";
import type { UsersCreateUserData } from "@/client";

export const useSignup = () => {
  return useMutation({
    mutationFn: (data: UsersCreateUserData) =>
      UsersService.createUser({ requestBody: data.requestBody }),
  });
};
