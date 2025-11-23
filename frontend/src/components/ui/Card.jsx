import React from 'react';
import PropTypes from 'prop-types';

/**
 * Card component for consistent container styling
 * Supports different padding sizes and hover effects
 */
const Card = ({
  children,
  title,
  subtitle,
  footer,
  padding = 'md',
  hoverable = false,
  className = '',
  ...props
}) => {
  const paddingSizes = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
    none: 'p-0',
  };
  
  const baseStyles = `
    bg-white rounded-lg shadow-sm border border-gray-200
    ${hoverable ? 'hover:shadow-md transition-shadow duration-200' : ''}
    ${className}
  `.trim().replace(/\s+/g, ' ');
  
  return (
    <div className={baseStyles} {...props}>
      {(title || subtitle) && (
        <div className={`border-b border-gray-200 ${paddingSizes[padding]}`}>
          {title && (
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          )}
          {subtitle && (
            <p className="mt-1 text-sm text-gray-600">{subtitle}</p>
          )}
        </div>
      )}
      
      <div className={title || subtitle ? paddingSizes[padding] : paddingSizes[padding]}>
        {children}
      </div>
      
      {footer && (
        <div className={`border-t border-gray-200 ${paddingSizes[padding]} bg-gray-50`}>
          {footer}
        </div>
      )}
    </div>
  );
};

Card.propTypes = {
  children: PropTypes.node.isRequired,
  title: PropTypes.string,
  subtitle: PropTypes.string,
  footer: PropTypes.node,
  padding: PropTypes.oneOf(['sm', 'md', 'lg', 'none']),
  hoverable: PropTypes.bool,
  className: PropTypes.string,
};

export default Card;
