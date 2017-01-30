import { createStore } from 'redux';

export const Modes = {
  VIEW,
  EDIT
};

export const Actions = {
  SET_PAGE,
  SET_MODE
};

const initialState = {
  page: {},
  mode: Modes.VIEW,
  identity: {}
};

export function setEditMode(mode) {
  return {
    type: Actions.SET_MODE,
    mode: mode
  };
}

export function setPage(page) {
  return {
    type: Actions.SET_PAGE,
    page: page
  };
}

export function WikiApp(state, action) {
  if (typeof state == 'undefined') {
    return initialState;
  }

  switch (action.type) {
    case SET_PAGE:
      return Object.assign({}, state, {
        page: action.page
      };
      break;
    case SET_MODE:
      return Object.assign({}, state, {
        mode: action.mode
      });
  }

  return state;
};
