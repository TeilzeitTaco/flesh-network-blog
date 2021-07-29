import {Component, EventEmitter, Input, Output} from '@angular/core';
import {Letter} from "../../shared/models/letter.model";


@Component({
  selector: 'app-letter-icon',
  templateUrl: './letter-icon.component.html',
  styleUrls: ['./letter-icon.component.css']
})
export class LetterIconComponent {
  @Input() letter!: Letter;
  @Output() clicked = new EventEmitter<void>()

  onClick(): void {
    this.clicked.emit()
  }
}
