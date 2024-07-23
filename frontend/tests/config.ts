const { FIRST_SUPERUSER, FIRST_SUPERUSER_PASSWORD } = process.env;

if (!FIRST_SUPERUSER || !FIRST_SUPERUSER_PASSWORD) {
  throw new Error("Environment variables FIRST_SUPERUSER or FIRST_SUPERUSER_PASSWORD are undefined");
}

export const firstSuperuser = FIRST_SUPERUSER as string;
export const firstSuperuserPassword = FIRST_SUPERUSER_PASSWORD as string;
