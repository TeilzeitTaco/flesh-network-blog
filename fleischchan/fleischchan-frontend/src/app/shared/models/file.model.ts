export class FileModel {
  constructor(public id: number, public hashOfContents: String, public originalName: String) {
  }

  getResourceUrl(): string {
    return `/api/v1/files/${this.hashOfContents}/content`
  }
}
