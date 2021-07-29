import {Injectable} from "@angular/core";
import {Letter} from "../shared/models/letter.model";
import {HttpClient} from "@angular/common/http";
import {map} from "rxjs/operators";
import {FileModel} from "../shared/models/file.model";

const ALL_LETTERS_ENDPOINT = "/api/v1/letters"
const ALL_FILES_ENDPOINT = "/api/v1/files/"


@Injectable({ providedIn: 'root' })
export class LettersService {
  constructor(private httpClient: HttpClient) {
  }

  uploadLetter(letter: any, image: File | null, callback: () => void) {
    // A nasty three-stage request. I won't fix this.
    // Firstly, post the letter.
    this.httpClient
      .post(ALL_LETTERS_ENDPOINT, letter)
      .subscribe((responseData: any) => {
        if (image == null) {
          callback()
          return;
        }

        alert(responseData.error)

        // Then, upload the image (if we have one).
        let formData = new FormData()
        formData.set("file", image)

        this.httpClient
          .post(ALL_FILES_ENDPOINT, formData)
          .subscribe(secondResponseData => {
            // Finally, attach the image to the letter.
            let letterUrl = `${ALL_LETTERS_ENDPOINT}/${responseData.id}/attachedImage`
            this.httpClient
              .put(letterUrl, secondResponseData)
              .subscribe(callback)
          })
      })
  }

  fetchLetters() {
    return this.httpClient
      .get(ALL_LETTERS_ENDPOINT)
      .pipe(
        map((responseData: any) => {
          const letters: Letter[] = []
          for (const key in responseData) {
            const data = responseData[key]

            // Maybe process the the file model.
            let fileModel: FileModel | null = null
            if (data.attachedImage != null) {
              fileModel = new FileModel(
                data.attachedImage.id,
                data.attachedImage.hashOfContents,
                data.attachedImage.originalName
              )
            }

            letters.push(new Letter(
              data.id, data.title, data.content, data.author, fileModel
            ))
          }

          return letters
        })
      )
  }
}
