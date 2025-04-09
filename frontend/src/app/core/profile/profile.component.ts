import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Subject, takeUntil } from 'rxjs';

interface UserProfile {
  username: string;
  email: string;
  // Add other profile properties if your backend returns them
}

interface ChatMessage {
  text: string;
  sender: 'user' | 'bot';
}

@Component({
  selector: 'app-profile',
  standalone: true,
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css'],
  imports: [CommonModule, FormsModule, RouterModule]
})
export class ProfileComponent implements OnInit, OnDestroy {
  profile: UserProfile = { username: '', email: '' };
  isEditing = false;
  editProfile: UserProfile = { username: '', email: '' };
  updateError = '';
  updateSuccess = '';
  showMenu = false;

  isChatbotEnabled: boolean = false; // Controls whether chatbot functionality is enabled
  isChatbotOpen = false; // Controls visibility of chat window
  chatMessages: ChatMessage[] = [];
  newMessage = '';
  showChatbotIcon: boolean = false; // Property to control chatbot icon visibility

  private ngUnsubscribe = new Subject<void>();

  constructor(private router: Router) {}

  ngOnInit(): void {
    this.loadProfile();
    this.loadChatbotSettings();
  }

  ngOnDestroy(): void {
    this.ngUnsubscribe.next();
    this.ngUnsubscribe.complete();
  }

  loadChatbotSettings(): void {
    const chatbotEnabled = localStorage.getItem('chatbotEnabled');
    this.isChatbotEnabled = chatbotEnabled === 'true';
  }

  saveChatbotSettings(): void {
    localStorage.setItem('chatbotEnabled', this.isChatbotEnabled.toString());
  }

  loadProfile(): void {
    const storedProfile = localStorage.getItem('userProfile');
    console.log('Stored Profile from localStorage:', storedProfile);
    if (storedProfile && storedProfile !== 'undefined') {
      try {
        this.profile = JSON.parse(storedProfile);
        this.editProfile = { ...this.profile };
        console.log('Loaded Profile:', this.profile);
      } catch (error) {
        console.error('Error parsing userProfile from localStorage:', error);
        this.router.navigate(['/login']);
      }
    } else {
      console.log('No userProfile found in localStorage, navigating to login.');
      this.router.navigate(['/login']);
    }
  }

  toggleMenu(): void {
    this.showMenu = !this.showMenu;
  }

  enableEditMode(): void {
    this.isEditing = true;
    this.editProfile = { ...this.profile };
    this.updateError = '';
    this.updateSuccess = '';
  }

  disableEditMode(): void {
    this.isEditing = false;
    this.updateError = '';
    this.updateSuccess = '';
    this.editProfile = { ...this.profile };
  }

  saveProfile(): void {
    console.log('Saving profile:', this.editProfile);
    this.updateSuccess = 'Profile updated successfully!';
    setTimeout(() => this.updateSuccess = '', 3000);
    this.isEditing = false;
    this.profile = { ...this.editProfile };
    localStorage.setItem('userProfile', JSON.stringify(this.profile));
  }

  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('userProfile');
    this.router.navigate(['/login']);
  }

  toggleChatbot(): void {
    if (this.isChatbotEnabled && this.showChatbotIcon) { // Only toggle if chatbot is enabled AND the icon is visible
      this.isChatbotOpen = !this.isChatbotOpen;
      if (this.isChatbotOpen && this.chatMessages.length === 0) {
        this.addBotMessage('Hello! How can I help you today?');
      }
    } else if (!this.isChatbotEnabled) {
      console.log('Chatbot is disabled.');
    } else if (!this.showChatbotIcon) {
      console.log('Chatbot icon is not visible.');
    }
  }

  closeChatbot(): void {
    this.isChatbotOpen = false;
  }

  sendMessage(): void {
    if (this.newMessage.trim() && this.isChatbotEnabled && this.showChatbotIcon) { // Only send if enabled and icon is visible
      this.addUserMessage(this.newMessage);
      this.getBotResponse(this.newMessage);
      this.newMessage = '';
    } else if (!this.isChatbotEnabled) {
      console.log('Chatbot is disabled.');
    } else if (!this.showChatbotIcon) {
      console.log('Chatbot icon is not visible.');
    }
  }

  addUserMessage(text: string): void {
    this.chatMessages.push({ text: text, sender: 'user' });
  }

  addBotMessage(text: string): void {
    this.chatMessages.push({ text: text, sender: 'bot' });
  }

  getBotResponse(userMessage: string): void {
    setTimeout(() => {
      const response = this.simulateBotResponse(userMessage);
      this.addBotMessage(response);
    }, 500);
  }

  simulateBotResponse(userMessage: string): string {
    userMessage = userMessage.toLowerCase();
    if (userMessage.includes('profile')) {
      return 'You are currently viewing your profile page.';
    } else if (userMessage.includes('edit')) {
      return 'You can edit your profile information using the form above.';
    } else if (userMessage.includes('settings')) {
      return 'You can manage your settings in the menu.';
    } else {
      return 'I am a simple chatbot and do not understand that query.';
    }
  }

  toggleChatbotEnabled(event: any): void {
    this.isChatbotEnabled = event.target.checked;
    this.saveChatbotSettings();
  }

  // Method to handle the chatbot icon toggle event from the header
  handleChatbotIconToggle(show: boolean) {
    this.showChatbotIcon = show;
    console.log('Chatbot Icon Visibility in Profile:', this.showChatbotIcon);
  }
}