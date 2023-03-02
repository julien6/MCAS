import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChartsVisualizationComponent } from './charts-visualization.component';

describe('ChartsVisualizationComponent', () => {
  let component: ChartsVisualizationComponent;
  let fixture: ComponentFixture<ChartsVisualizationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ChartsVisualizationComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChartsVisualizationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
