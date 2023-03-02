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
import { HttpClient } from '@angular/common/http';
import { HttpClientModule } from '@angular/common/http';
import { ChartsVisualizationComponent } from './charts-visualization/charts-visualization.component';
import { NgChartsModule } from 'ng2-charts';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { MatTabsModule } from '@angular/material/tabs';

@NgModule({
  declarations: [
    AppComponent,
    DetailPanelComponent,
    GraphComponent,
    TerminalComponent,
    ChartsVisualizationComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    AngJsoneditorModule,
    NgTerminalModule,
    HttpClientModule,
    NgChartsModule,
    NoopAnimationsModule,
    MatTabsModule
  ],
  providers: [AppNetworkService, WorldStateService, ServerAPIService, HttpClient],
  bootstrap: [AppComponent]
})
export class AppModule { }
