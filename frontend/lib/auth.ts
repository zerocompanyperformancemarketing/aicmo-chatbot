export function getToken(): string | null {
  return localStorage.getItem('token');
}

export function getUsername(): string | null {
  return localStorage.getItem('username');
}

export function getFullName(): string | null {
  return localStorage.getItem('fullName');
}

export function isAuthenticated(): boolean {
  return !!getToken();
}

export function logout(): void {
  localStorage.removeItem('token');
  localStorage.removeItem('username');
  localStorage.removeItem('fullName');
  sessionStorage.removeItem('conversationId');
}
