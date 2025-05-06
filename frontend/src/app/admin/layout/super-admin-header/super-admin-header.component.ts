import { Component, OnInit } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { HttpClient } from '@angular/common/http';  // To make HTTP requests
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-super-admin-header',
  standalone: true,
  templateUrl: './super-admin-header.component.html',
  styleUrls: ['./super-admin-header.component.css'],
  imports: [RouterModule, CommonModule]
})
export class SuperAdminHeaderComponent implements OnInit {
  userRole: string | null = null;

  constructor(private router: Router, private http: HttpClient) {
    console.log('SuperAdminHeaderComponent initialized.');
  }

  ngOnInit(): void {
    // Fetching user role from local storage
    this.userRole = localStorage.getItem('role');
    console.log('User Role:', this.userRole);
  }

  logout() {
    // Clear the auth token and user role from local storage
    localStorage.removeItem('authToken');
    localStorage.removeItem('role');
    this.router.navigate(['/login']);  // Navigate to the login page
  }

  // Method to handle the download of the config file
  // Function to fetch the access key and trigger the file download
  downloadConfig() {
    this.http.get('http://localhost:5000/api/download-config', {
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('authToken')
        }
    })
    .subscribe(
        (response: any) => {
            if (response && response.access_key) {
                const access_key = response.access_key;
                // Generate the script with the access key
                const scriptContent = `<script init_key="${access_key}" src="http://localhost:4200/chatbot.js"></script>`;
                
                // Create a Blob with the script content
                const blob = new Blob([scriptContent], { type: 'text/plain' });

                // Create an anchor element and simulate a click to trigger the download
                const link = document.createElement('a');
                link.href = URL.createObjectURL(blob);
                link.download = 'config.txt';  // The file name
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            } else {
                alert('Error: Access key not received');
            }
        },
        (error) => {
            console.error('Error downloading config:', error);
            alert('Error downloading the config file');
        }
    );
}
}
