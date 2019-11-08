import {combineReducers} from "redux"

import {timestamp} from "./utils.js"

function activities(state = [], action) {
  switch (action.type) {
    case "ADD_ACTIVITY":
      return state.concat([action.activity])
    case "REMOVE_ACTIVITY":
      return state.filter(activity => activity.id != action.id)
    case "UPDATE_ACTIVITY":
      return state.map(activity =>
        activity.id == action.id ? {...activity, ...action.fields} : activity
      )
    case "START":
    case "STOP":
      return action.current
        ? state.map(activity =>
            activity.id == action.current.id
              ? {
                  ...activity,
                  seconds:
                    activity.seconds + (timestamp() - action.current.startedAt),
                }
              : activity
          )
        : state
    default:
      return state
  }
}

function current(state = null, action) {
  switch (action.type) {
    case "START":
      return {
        id: action.id,
        startedAt: timestamp(),
      }
    case "STOP":
      return null
    default:
      return state
  }
}

function modalActivity(state = null, action) {
  switch (action.type) {
    case "MODAL_ACTIVITY":
      return action.id
    case "UPDATE_ACTIVITY":
      return null
    default:
      return state
  }
}

function projects(state = [], action) {
  switch (action.type) {
    case "PROJECTS":
      return action.projects
    default:
      return state
  }
}

const reducer = combineReducers({
  activities,
  current,
  modalActivity,
  projects,
})

export default reducer