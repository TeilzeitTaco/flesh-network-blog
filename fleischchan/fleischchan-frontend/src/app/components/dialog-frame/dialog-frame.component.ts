import {Component, ElementRef, OnInit, TemplateRef, ViewChild, ViewContainerRef} from '@angular/core';

@Component({
  selector: 'app-dialog-frame',
  templateUrl: './dialog-frame.component.html',
  styleUrls: ['./dialog-frame.component.css']
})
export class DialogFrameComponent implements OnInit {
  @ViewChild("container", {read: ViewContainerRef}) container!: ViewContainerRef
  @ViewChild(TemplateRef) template!: TemplateRef<any>;

  set showDialog(state: boolean) {
    if (state) {
      this.container.createEmbeddedView(this.template)
    } else {
      this.container.clear()
    }
  }

  onBackgroundClicked(): void {
    this.showDialog = false
  }

  ngOnInit(): void {
  }
}
