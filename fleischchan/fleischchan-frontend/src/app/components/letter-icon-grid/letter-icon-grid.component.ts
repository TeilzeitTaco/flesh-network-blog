import { EventEmitter, Output } from '@angular/core';
import { Component} from '@angular/core';
import { Letter } from "../../shared/models/letter.model";

@Component({
  selector: 'app-letter-icon-grid',
  templateUrl: './letter-icon-grid.component.html',
  styleUrls: ['./letter-icon-grid.component.css']
})
export class LetterIconGridComponent {
  @Output() newLetterClicked = new EventEmitter<void>()
  @Output() viewLetterClicked = new EventEmitter<Letter>()

  letters: Letter[] = []

  onNewLetter(): void {
    this.newLetterClicked.emit()
  }

  onViewLetter(letter: Letter): void {
    this.viewLetterClicked.emit(letter)
  }
}
