import PropTypes from 'prop-types'
import { Navigate } from 'react-router-dom'
import { isAuthenticated } from '../api/auth'

export default function RequireAuth({ children }) {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />
  }
  return children
}

RequireAuth.propTypes = {
  children: PropTypes.node.isRequired,
}
