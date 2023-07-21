import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { AngJsoneditorModule } from '@maaxgr/ang-jsoneditor';
import { DetailPanelComponent } from './detail-panel/detail-panel.component'
import { AppNetworkService } from './services/app.network.service';
import { WorldStateService } from './services/app.worldState.service';
import { GraphComponent } from './graph/graph.component';
import { TerminalComponent } from './terminal/terminal.component';
import { NgTerminalModule } from 'ng-terminal';
import { ServerAPIService } from './services/serverAPI.service';
import { ChartsVisualizationComponent } from './charts-visualization/charts-visualization.component';
import { NgChartsModule } from 'ng2-charts';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { LayoutModule } from '@angular/cdk/layout';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatMenuModule } from '@angular/material/menu';
import { MenuBarComponent } from './menu-bar/menu-bar.component';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDialogModule } from '@angular/material/dialog';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatNativeDateModule } from '@angular/material/core';
import { PreferencesComponent } from './preferences/preferences.component';
import { LibraryComponent } from './library/library.component';
import { PropertiesComponent } from './properties/properties.component';
import { HistoryComponent } from './history/history.component';
import { MatCardModule } from '@angular/material/card';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatTabsModule } from '@angular/material/tabs';
import { MatRippleModule } from '@angular/material/core';
import { LibraryElementComponent } from './library-element/library-element.component'
import { MarkdownModule } from 'ngx-markdown';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

@NgModule({
  declarations: [
    AppComponent,
    DetailPanelComponent,
    GraphComponent,
    TerminalComponent,
    ChartsVisualizationComponent,
    AppComponent,
    MenuBarComponent,
    PreferencesComponent,
    LibraryComponent,
    PropertiesComponent,
    HistoryComponent,
    LibraryElementComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    AngJsoneditorModule,
    NgTerminalModule,
    HttpClientModule,
    NgChartsModule,
    NoopAnimationsModule,
    MatTabsModule,
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    HttpClientModule,
    MarkdownModule.forRoot({ loader: HttpClient }),
    MatTabsModule,
    MatRippleModule,
    MatSlideToggleModule,
    LayoutModule,
    MatToolbarModule,
    FormsModule,
    MatButtonModule,
    MatSidenavModule,
    MatIconModule,
    MatCardModule,
    MatListModule,
    MatGridListModule,
    MatMenuModule,
    MatCheckboxModule,
    MatDialogModule,
    MatButtonModule,
    MatExpansionModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatDatepickerModule,
    MatNativeDateModule
  ],
  providers: [AppNetworkService, WorldStateService, ServerAPIService, HttpClient],
  bootstrap: [AppComponent]
})
export class AppModule { }
