import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NgHttpLoaderComponent } from 'ng-http-loader'; // Import the ng-http-loader component

@Component({
  selector: 'app-root',
  standalone: true, // Keep this as true for standalone component
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  imports: [RouterOutlet, NgHttpLoaderComponent], // Add NgHttpLoaderComponent to the imports array
})
export class AppComponent {}
