import {AbsoluteFill} from 'remotion';

// A small, renderable placeholder used only to verify that Remotion is wired up.
export const BootstrapComposition: React.FC = () => (
  <AbsoluteFill
    style={{
      alignItems: 'center',
      backgroundColor: '#f4f1e8',
      color: '#252a2a',
      display: 'flex',
      fontFamily: 'Arial, sans-serif',
      fontSize: 56,
      fontWeight: 700,
      justifyContent: 'center',
    }}
  >
    AI Video Maker
  </AbsoluteFill>
);