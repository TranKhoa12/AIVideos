import {registerRoot} from 'remotion';
import {RemotionRoot} from './Root';

// Keep one stable Remotion entry point so jobs can select compositions consistently.
registerRoot(RemotionRoot);