const { FIRST_SUPERUSER, FIRST_SUPERUSER_PASSWORD } = process.env;

if (!FIRST_SUPERUSER) {
  throw new Error("Environment variable FIRST_SUPERUSER is undefined");
}

if (!FIRST_SUPERUSER_PASSWORD) {
  throw new Error("Environment variable FIRST_SUPERUSER_PASSWORD is undefined");
}

export const firstSuperuser = FIRST_SUPERUSER as string;
export const firstSuperuserPassword = FIRST_SUPERUSER_PASSWORD as string;
