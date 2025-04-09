import { Routes } from '@angular/router';
import { LoginComponent } from './core/login/login.component';
import { DashboardComponent } from './admin/dashboard/dashboard.component';
import { UsersComponent } from './admin/users/users.component';
import { InviteComponent } from './admin/invite/invite.component';
import {MonitorComponent} from './admin/monitor/monitor.component';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'admin/dashboard', component: DashboardComponent },
  {
    path: 'admin/users',
    component: UsersComponent
  },
  { path: 'admin/invite', component: InviteComponent },
  { path: 'admin/monitor', component: MonitorComponent }
];
