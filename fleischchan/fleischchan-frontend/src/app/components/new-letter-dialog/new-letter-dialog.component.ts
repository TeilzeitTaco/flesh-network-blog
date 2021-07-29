import {Component, ElementRef, EventEmitter, OnInit, Output} from '@angular/core';
import {NgForm} from "@angular/forms";
import {Letter} from "../../shared/models/letter.model";
import {LettersService} from "../../services/letters.service";
import {delay} from "rxjs/operators";

@Component({
  selector: 'app-new-letter-dialog',
  templateUrl: './new-letter-dialog.component.html',
  styleUrls: ['./new-letter-dialog.component.css']
})
export class NewLetterDialogComponent implements OnInit {
  @Output() newLetterCreated = new EventEmitter<Letter>()
  @Output() newLetterPosted = new EventEmitter<void>()

  private selectedFile: File | null = null

  constructor(private lettersService: LettersService) { }

  ngOnInit(): void {
  }

  onSubmit(form: NgForm): void {
    let {author, title, content} = form.form.value
    let cleanedContent = content.replace(/([ !?()]){2,}/, "$1")

    let letter = new Letter(0, title, cleanedContent, author, null,
      true, this.selectedFile != null)

    this.newLetterCreated.emit(letter)
    this.lettersService.uploadLetter(letter, this.selectedFile, () => {
      this.newLetterPosted.emit()
    })
  }

  onFileSelected(files: any) {
    this.selectedFile = files.files[0]
  }
}
