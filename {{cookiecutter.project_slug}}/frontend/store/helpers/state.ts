export interface HelperState {
  headingTitle: string | null
}

const defaultState: HelperState = {
  headingTitle: null,
}

export default () => defaultState
