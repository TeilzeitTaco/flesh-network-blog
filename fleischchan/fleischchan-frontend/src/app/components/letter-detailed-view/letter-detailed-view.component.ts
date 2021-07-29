import {Component, Input, OnInit} from '@angular/core';
import {Letter} from "../../shared/models/letter.model";

@Component({
  selector: 'app-letter-detailed-view',
  templateUrl: './letter-detailed-view.component.html',
  styleUrls: ['./letter-detailed-view.component.css']
})
export class LetterDetailedViewComponent {
  @Input() letter!: Letter;
}
