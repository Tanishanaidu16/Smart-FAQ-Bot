import { Routes } from '@angular/router';
import { LoginComponent } from './core/login/login.component';
import { DashboardComponent } from './admin/dashboard/dashboard.component';
import { UsersComponent } from './admin/users/users.component';
import { InviteComponent } from './admin/invite/invite.component';
import { MonitorComponent } from './admin/monitor/monitor.component';
import { ProfileComponent } from './core/profile/profile.component';
import { LayoutComponent } from './layout/layout.component'; // Import LayoutComponent

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  {
    path: '',
    component: LayoutComponent, // Use LayoutComponent as the parent for routes with header
    children: [
      { path: 'admin/dashboard', component: DashboardComponent },
      { path: 'admin/users', component: UsersComponent },
      { path: 'admin/invite', component: InviteComponent },
      { path: 'admin/monitor', component: MonitorComponent },
      { path: 'core/profile', component: ProfileComponent },
      // Add other routes that should be within the layout here
    ],
  },
  // You can add other routes that don't need the layout outside of the 'children' array
];