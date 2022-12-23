import { Wrapper, WrapperArray } from "@vue/test-utils";

export function flushPromises() {
  return new Promise(function (resolve) {
    setTimeout(resolve);
  });
}

// Vue test utils component selection

export function componentWithText(
  wrapperArray: WrapperArray<Vue>,
  text: string,
): Wrapper<Vue> {
  return wrapperArray.filter((c) => c.text().includes(text)).at(0);
}
