import {FileModel} from "./file.model";

const SIZE_THRESHOLD = 256


export class Letter {
  constructor(public id: number, public title: string,
              public content: string, public author: string,
              public fileModel: FileModel | null,

              // These two do not correspond to fields on the backend.
              // They just exist so we can do some special things in the
              // UI when a letter is submitted.
              public isEphemeral: boolean = false,
              public willHaveImage: boolean = false) {}

  public sample(): string {
    if (this.content.length > SIZE_THRESHOLD) {
      let buffer = ""
      const words = this.content.split(" ")
      for (let word of words) {
        if (buffer.length + word.length >= SIZE_THRESHOLD)
          break;

        buffer += " " + word
      }

      return buffer + "..."
    }

    return this.content
  }
}
