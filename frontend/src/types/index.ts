export interface User {
  telegram_id: number;
  first_name: string;
  username?: string;
}

export interface Project {
  id: string;
  name: string;
  status: 'PENDING' | 'PROCESSING' | 'RUNNING' | 'STOPPED' | 'FAILED';
  created_at: string;
  updated_at: string;
  last_error_log?: string;
  container_id?: string;
}

export interface TelegramAuthData {
  id: string;
  first_name: string;
  username?: string;
  photo_url?: string;
  auth_date: string;
  hash: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ProjectsResponse {
  projects: Project[];
}

export interface CreateProjectResponse {
  message: string;
  project_id: string;
  status: string;
}