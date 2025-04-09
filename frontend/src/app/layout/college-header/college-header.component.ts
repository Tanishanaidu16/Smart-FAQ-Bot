import { Component, Output, EventEmitter } from '@angular/core';
import { Router, RouterModule, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-college-header',
  standalone: true,
  templateUrl: './college-header.component.html',
  styleUrls: ['./college-header.component.css'],
  imports: [RouterModule, CommonModule]
})
export class CollegeHeaderComponent {
  @Output() chatbotIconToggled = new EventEmitter<boolean>();
  enableChatbotIcon: boolean = false;

  constructor(public router: Router) {
    console.log('CollegeHeaderComponent initialized.'); // Console log in constructor
  }

  toggleChatbotIcon() {
    this.enableChatbotIcon = !this.enableChatbotIcon;
    this.chatbotIconToggled.emit(this.enableChatbotIcon);
    console.log('Chatbot Icon Enabled:', this.enableChatbotIcon);
  }

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    this.router.navigate(['/login']);
  }
}