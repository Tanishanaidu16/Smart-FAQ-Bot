import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
// import { HeaderComponent } from '../../header1/header/header.component';
import { FooterComponent } from '../../footer/footer.component';

@Component({
  selector: 'app-invite',
  standalone: true,
  imports: [CommonModule, FooterComponent],
  templateUrl: './invite.component.html',
  styleUrls: ['./invite.component.css']
})
export class InviteComponent {}
