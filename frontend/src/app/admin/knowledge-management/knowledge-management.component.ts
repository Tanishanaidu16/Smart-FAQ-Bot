import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-knowledge-management',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './knowledge-management.component.html',
  styleUrls: ['./knowledge-management.component.css']
})
export class KnowledgeManagementComponent {
  welcomeMessage: string = 'Welcome to Knowledge Management!';
}