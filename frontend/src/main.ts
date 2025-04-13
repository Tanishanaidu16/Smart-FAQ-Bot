import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { provideHttpClient, withInterceptors } from '@angular/common/http'; // Import HTTP client and interceptor
import { provideRouter } from '@angular/router';
import { provideAnimations } from '@angular/platform-browser/animations'; // Import animations provider
import { routes } from './app/app.routes';
import { pendingRequestsInterceptor$ } from 'ng-http-loader'; // Import the HTTP loader interceptor

bootstrapApplication(AppComponent, {
  providers: [
    provideHttpClient(withInterceptors([pendingRequestsInterceptor$])), // Use the interceptor here
    provideRouter(routes),
    provideAnimations(), // Include animations provider
  ]
});
