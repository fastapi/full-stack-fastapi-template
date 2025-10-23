"use client";
import Input from "@/components/form/input/InputField";
import Label from "@/components/form/Label";
import { ChevronLeftIcon, EyeCloseIcon, EyeIcon } from "@/icons";
import Link from "next/link";
import React, { useEffect, useState } from "react";
import { namePattern, emailPattern, passwordRules } from "@/utils";
import { type SubmitHandler, useForm } from "react-hook-form"
import useAuth, { isLoggedIn } from "@/hooks/useAuth";
import type { UserRegister } from "@/client";
import SpinnerButton from "../ui/button/SpinnerButton";
import { useRouter } from "next/navigation";



type FormData = {
  firstName: string;
  lastName: string;
  password: string;
  email: string;
};

export default function SignUpForm() {
  const [showPassword, setShowPassword] = useState(false);

  const { signUpMutation } = useAuth();
  const router = useRouter();


    useEffect(() => {
      if (isLoggedIn()) {
        router.push("/");
      }
    }, [router])


  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    mode: "onChange"
  });
  const onSubmit: SubmitHandler<FormData> = (data) => {
    const payload: UserRegister = {
      full_name: `${data.firstName} ${data.lastName}`,
      email: data.email,
      password: data.password,
    };

    signUpMutation.mutate(payload);
  };

  return (
    <div className="flex flex-col flex-1 lg:w-1/2 w-full overflow-y-auto no-scrollbar">
      <div className="w-full max-w-md sm:pt-10 mx-auto mb-5">
        <Link
          href="/"
          className="inline-flex items-center text-sm text-gray-500 transition-colors hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
        >
          <ChevronLeftIcon />
          Back to home
        </Link>
      </div>

      <div className="flex flex-col justify-center flex-1 w-full max-w-md mx-auto">
        <div className="mb-5 sm:mb-8">
          <h1 className="mb-2 font-semibold text-gray-800 text-title-sm dark:text-white/90 sm:text-title-md">
            Sign Up
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Enter your name to sign up!
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            {/* First Name */}
            <div>
              <Label>
                First Name<span className="text-error-500">*</span>
              </Label>
              <Input
                placeholder="Enter your first name"
                {...register("firstName", {
                  required: "First name is required",
                  pattern: namePattern,
                })}
                error={!!errors.firstName}
                hint={errors.firstName?.message}
              />
            </div>

            {/* Last Name */}
            <div>
              <Label>
                Last Name<span className="text-error-500">*</span>
              </Label>
              <Input
                placeholder="Enter your last name"
                {...register("lastName", {
                  required: "Last name is required",
                  pattern: namePattern,
                })}
                error={!!errors.lastName}
                hint={errors.lastName?.message}
              />
            </div>
            {/* Email */}
            <div className="sm:col-span-2">
              <Label>
                Email<span className="text-error-500">*</span>
              </Label>
              <Input
                placeholder="Enter your email"
                type="email"
                {...register("email", {
                  required: "Email is required",
                  pattern: emailPattern
                })}
                error={!!errors.email}
                hint={errors.email?.message}
              />
            </div>
            {/* Password */}
            <div className="sm:col-span-2">
              <Label>
                Password<span className="text-error-500">*</span>
              </Label>
              <div className="relative">
                <Input
                  placeholder="Enter your password"
                  type={showPassword ? "text" : "password"}
                  {...register("password", passwordRules())}
                  error={!!errors.password}
                  hint={errors.password?.message}
                />
                <span
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute z-30 cursor-pointer right-4 top-1/2 -translate-y-1/2"
                >
                  {showPassword ? (
                    <EyeIcon className="fill-gray-500 dark:fill-gray-400" />
                  ) : (
                    <EyeCloseIcon className="fill-gray-500 dark:fill-gray-400" />
                  )}
                </span>
              </div>
            </div>
            {/* Submit Button */}
            <div className="sm:col-span-2">
              <SpinnerButton
                className="flex items-center justify-center w-full px-4 py-3 text-sm font-medium text-white transition rounded-lg bg-brand-500 shadow-theme-xs hover:bg-brand-600"
                disabled={!!errors.firstName || !!errors.lastName || !!errors.email || !!errors.password}
                loading={isSubmitting}
              >
                Sign Up
              </SpinnerButton>
            </div>
          </div>
        </form>
        <div className="mt-5">
          <p className="text-sm font-normal text-center text-gray-700 dark:text-gray-400 sm:text-start">
            Already have an account?{" "}
            <Link
              href="/signin"
              className="text-brand-500 hover:text-brand-600 dark:text-brand-400"
            >
              Sign In
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
