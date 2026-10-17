import {Composition} from 'remotion';
import {BootstrapComposition} from './compositions/BootstrapComposition';
import {LocalCompositions} from './generated/local-compositions';

export const RemotionRoot: React.FC = () => (
  <>
    <LocalCompositions/>
    <Composition
      id="BootstrapComposition"
      component={BootstrapComposition}
      durationInFrames={30}
      fps={30}
      width={1080}
      height={1920}
    />
  </>
);
