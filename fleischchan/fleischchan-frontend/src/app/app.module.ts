import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppComponent } from './app.component';
import { LetterIconGridComponent } from './components/letter-icon-grid/letter-icon-grid.component';
import { LetterIconComponent } from './components/letter-icon/letter-icon.component';
import { FooterComponent } from './components/footer/footer.component';
import {BasicHighlightDirective} from "./directives/basic-highlight/basic-highlight.directive";
import { BetterHighlightDirective } from './directives/better-highlight/better-highlight.directive';
import { UnlessDirective } from './directives/unless/unless.directive';
import {RouterModule, Routes} from "@angular/router";
import { DialogFrameComponent } from './components/dialog-frame/dialog-frame.component';
import { NewLetterDialogComponent } from './components/new-letter-dialog/new-letter-dialog.component';
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {HttpClientModule} from "@angular/common/http";
import { InfoPageComponentComponent } from './components/info-page-component/info-page-component.component';
import { HomePageComponentComponent } from './components/home-page-component/home-page-component.component';
import { LetterDetailedViewComponent } from './components/letter-detailed-view/letter-detailed-view.component';
import { DialogComponent } from './components/dialog/dialog.component';
import {MarkdownModule, MarkdownService} from "ngx-markdown";

const appRoutes: Routes = [
  { path: "", component: HomePageComponentComponent },
  { path: "info", component: InfoPageComponentComponent }
]


@NgModule({
  declarations: [
    AppComponent,
    LetterIconGridComponent,
    LetterIconComponent,
    FooterComponent,
    BasicHighlightDirective,
    BetterHighlightDirective,
    UnlessDirective,
    DialogFrameComponent,
    NewLetterDialogComponent,
    InfoPageComponentComponent,
    HomePageComponentComponent,
    LetterDetailedViewComponent,
    DialogComponent,
  ],
  imports: [
    BrowserModule,
    RouterModule.forRoot(appRoutes),
    MarkdownModule.forRoot(),
    ReactiveFormsModule,
    FormsModule,
    HttpClientModule,
    MarkdownModule
  ],
  providers: [
    MarkdownService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
