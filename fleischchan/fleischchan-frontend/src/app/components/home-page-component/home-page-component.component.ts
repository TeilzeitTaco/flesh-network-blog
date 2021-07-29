import {Component, OnInit, ViewChild} from '@angular/core';
import {LettersService} from "../../services/letters.service";
import {DialogFrameComponent} from "../dialog-frame/dialog-frame.component";
import {LetterIconGridComponent} from "../letter-icon-grid/letter-icon-grid.component";
import {Letter} from "../../shared/models/letter.model";


@Component({
  selector: 'app-home-page-component',
  templateUrl: './home-page-component.component.html',
  styleUrls: ['./home-page-component.component.css']
})
export class HomePageComponentComponent implements OnInit {
  dialogType: number = 1
  selectedLetter: Letter | null = null

  constructor(private lettersService: LettersService) {
  }

  ngOnInit(): void {
    this.fetchPosts()
  }

  @ViewChild("dialogComponent") dialogComponent!: DialogFrameComponent;
  @ViewChild("letterIconGridComponent") letterIconGridComponent!: LetterIconGridComponent

  onNewLetterButtonClicked(): void {
    this.dialogType = 1
    this.dialogComponent.showDialog = true
  }

  onNewLetterCreated(letter: Letter): void {
    this.letterIconGridComponent.letters.unshift(letter)
    this.dialogComponent.showDialog = false
  }

  onViewLetterClicked(letter: Letter): void {
    this.selectedLetter = letter
    this.dialogType = 2
    this.dialogComponent.showDialog = true
  }

  fetchPosts(): void {
    this.lettersService.fetchLetters().subscribe(responseData => {
      this.letterIconGridComponent.letters = responseData
    })
  }
}

