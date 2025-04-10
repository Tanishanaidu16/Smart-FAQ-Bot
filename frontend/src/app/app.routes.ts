import { Routes } from '@angular/router';
import { LoginComponent } from './core/login/login.component';
import { LayoutComponent } from './admin/layout/layout.component';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  {
    path: 'admin',
    component: LayoutComponent,
    loadChildren: () => import('./admin/admin.module').then(m => m.AdminModule)
  }
];